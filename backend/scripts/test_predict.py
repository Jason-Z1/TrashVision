"""
Simple smoke-test script that POSTs a sample image to the local /predict endpoint and prints the response.
Usage:
python backend/scripts/test_predict.py path/to/test.jpg
"""
import sys
import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, world! The server is running."

# CORS handling
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def run_prediction(image):
    """
    Returns:
        dict: Prediction results with detected items and recommendations
    """
    try:
        # Get environment variables - Try Training Key if Prediction Key fails
        prediction_key = os.getenv('PREDICTION_KEY')
        training_key = os.getenv('TRAINING_KEY')  # Fallback option
        prediction_endpoint = os.getenv('PREDICTION_ENDPOINT') 
        project_id = os.getenv('PROJECT_ID')
        published_name = os.getenv('PUBLISHED_NAME', 'trashvision-v1')
        
        # Common iteration names to try if the provided one fails
        iteration_names_to_try = [
            published_name,
            'RecycleSmart-Prediction',
            'RecycleSmart'
        ]
        
        # Basic configuration validation
        if not all([prediction_key, prediction_endpoint, project_id]):
            print(f"Missing configuration - Endpoint: {bool(prediction_endpoint)}, Project: {bool(project_id)}, Key: {bool(prediction_key)}")
        
        # Validate required environment variables
        if not all([prediction_key, prediction_endpoint, project_id]):
            return {
                'error': 'Missing required environment variables: PREDICTION_KEY, ENDPOINT, PROJECT_ID'
            }
        
        # Ensure endpoint doesn't end with slash
        if prediction_endpoint.endswith('/'):
            prediction_endpoint = prediction_endpoint.rstrip('/')
        
        # Prepare headers
        headers = {
            'Prediction-Key': prediction_key,
            'Content-Type': 'application/octet-stream'
        }
        
        # Read image data
        image_data = image.read()
        
        # Try different iteration names until one works
        successful_response = None
        
        # Try with Prediction Key first, then Training Key as fallback
        keys_to_try = [
            ('Prediction-Key', prediction_key),
            ('Training-Key', training_key)
        ]
        
        for key_type, api_key in keys_to_try:
            if not api_key:
                continue
                
            headers = {
                key_type: api_key,
                'Content-Type': 'application/octet-stream'
            }
            
            for iteration_name in iteration_names_to_try:
                prediction_url = f"{prediction_endpoint}/customvision/v3.0/Prediction/{project_id}/classify/iterations/{iteration_name}/image"
                
                try:
                    response = requests.post(prediction_url, headers=headers, data=image_data, timeout=10)
                    
                    if response.status_code == 200:
                        print(f"Prediction successful with {iteration_name}")
                        successful_response = response
                        break
                    # Only log if not the expected first attempt
                    elif response.status_code != 200 and iteration_name == published_name:
                        print(f"Primary iteration failed: {response.status_code}")
                        continue
                    else:
                        continue
                        
                except Exception as e:
                    # Only log network errors for primary iteration
                    if iteration_name == published_name:
                        print(f"Network error: {e}")
                    continue
            
            # If we found a working response, break out of key loop too        
            if successful_response:
                break
        
        # Process successful response
        if successful_response and successful_response.status_code == 200:
            prediction_result = successful_response.json()
            
            # Process the prediction results
            detected_items = []
            recommendations = []
            
            # Get the highest confidence prediction
            if 'predictions' in prediction_result:
                predictions = prediction_result['predictions']
                
                # Sort by probability (highest first)
                predictions.sort(key=lambda x: x['probability'], reverse=True)
                
                for pred in predictions:
                    if pred['probability'] > 0.5:  # Only include predictions with >50% confidence
                        is_recyclable = pred['tagName'].lower() == 'recyclable'
                        
                        detected_items.append({
                            'type': pred['tagName'].lower(),
                            'confidence': pred['probability'],
                            'recyclable': is_recyclable
                        })
                        
                        # Generate recommendations based on prediction
                        if is_recyclable:
                            recommendations.append(f"{pred['tagName']} item can be placed in recycling bin")
                        else:
                            recommendations.append(f"{pred['tagName']} item should go in general waste")
            
            # If no high-confidence predictions, provide default response
            if not detected_items:
                detected_items.append({
                    'type': 'unknown',
                    'confidence': 0.0,
                    'recyclable': False
                })
                recommendations.append('Unable to classify item. Please check local recycling guidelines.')
            
            # Print detected items for debugging
            print(f"\n=== DETECTED ITEMS ===")
            for i, item in enumerate(detected_items):
                print(f"Item {i+1}: {item['type']} (confidence: {item['confidence']:.2%}, recyclable: {item['recyclable']})")
            print(f"\n=== RECOMMENDATIONS ===")
            for j, rec in enumerate(recommendations):
                print(f"{j+1}. {rec}")
            print(f"\n=== RAW PREDICTIONS ===")
            for k, pred in enumerate(prediction_result.get('predictions', [])):
                print(f"Prediction {k+1}: {pred.get('tagName')} - {pred.get('probability'):.2%}")
            
            return {
                'detected_items': detected_items,
                'recommendations': recommendations,
                'raw_predictions': prediction_result.get('predictions', [])
            }
        else:
            # If no iteration worked, return helpful error
            return {
                'error': 'No working iteration found. Check your Azure Custom Vision project.',
                'tried_iterations': iteration_names_to_try,
                'suggestion': 'Go to Azure Custom Vision portal > Performance tab > check your published iteration name'
            }
    except Exception as e:
        return {
            'error': f'Prediction failed: {str(e)}'
        }


@app.route('/predict', methods=['POST'])

def predict_image():
    """Endpoint for image classification."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    result = run_prediction(image)
    return jsonify(result)

def test_prediction_endpoint(image_path):
    """Test the /predict endpoint with a local image file."""
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            print(f"Error: File {image_path} not found")
            return
        
        # Prepare the test request
        url = 'http://localhost:5000/predict'
        with open(image_path, 'rb') as image_file:
            files = {'image': image_file}
            
            print(f"Testing prediction with image: {image_path}")
            print("Sending request to http://localhost:5000/predict...")
            
            response = requests.post(url, files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print("\n=== PREDICTION RESULTS ===")
                print(f"Detected Items: {result.get('detected_items', [])}")
                print(f"Recommendations: {result.get('recommendations', [])}")
                print("\n=== RAW PREDICTIONS ===")
                for pred in result.get('raw_predictions', []):
                    print(f"Tag: {pred.get('tagName')}, Confidence: {pred.get('probability'):.2%}")
            else:
                print(f"Error: {response.status_code} - {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Flask server. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"Test failed: {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        # Start the Flask server
        print("Starting Flask server for predictions...")
        print("Server will be available at: http://localhost:5000")
        print("To test with an image, run: python test_predict.py path/to/image.jpg")
        app.run(debug=True, port=5000)
    else:
        # Test mode - send an image to the server
        image_path = sys.argv[1]
        test_prediction_endpoint(image_path)
