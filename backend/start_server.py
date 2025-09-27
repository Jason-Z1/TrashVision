import os
import sys

# Add the scripts directory to Python path
scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
sys.path.insert(0, scripts_dir)

# Import and run the prediction server
from test_predict import app

if __name__ == '__main__':
    print("Starting TrashVision Prediction Server...")
    print("Server will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)