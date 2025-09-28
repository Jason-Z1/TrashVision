"""
Script to check Azure Custom Vision project details including:
- Project information
- Published iteration names
- Available iterations
- Model performance metrics
"""
import os
from dotenv import load_dotenv
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
from pathlib import Path

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def check_project_details():
    """Check all project details and published iterations"""
    
    # Get credentials from environment
    training_key = os.getenv('TRAINING_KEY')
    prediction_key = os.getenv('PREDICTION_KEY')
    endpoint = os.getenv('ENDPOINT')
    project_id = os.getenv('PROJECT_ID')
    
    if not all([training_key, endpoint, project_id]):
        print("❌ Missing required environment variables!")
        return
    
    try:
        # Initialize training client
        credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
        trainer = CustomVisionTrainingClient(endpoint, credentials)
        
        print("=" * 60)
        print("🔍 AZURE CUSTOM VISION PROJECT DETAILS")
        print("=" * 60)
        
        # Get project information
        project = trainer.get_project(project_id)
        print(f"📋 Project Name: {project.name}")
        print(f"🆔 Project ID: {project.id}")
        print(f"📝 Description: {project.description}")
        print(f"🏷️ Domain: {project.domain.name if project.domain else 'General'}")
        print(f"📅 Created: {project.created}")
        print(f"📊 Classification Type: {project.classification_type}")
        print()
        
        # Get all iterations
        print("🔄 ALL ITERATIONS:")
        print("-" * 40)
        iterations = trainer.get_iterations(project_id)
        
        if not iterations:
            print("❌ No iterations found!")
            return
            
        for i, iteration in enumerate(iterations, 1):
            print(f"{i}. Name: {iteration.name}")
            print(f"   ID: {iteration.id}")
            print(f"   Status: {iteration.status}")
            print(f"   Created: {iteration.created}")
            print(f"   Is Default: {iteration.is_default}")
            print(f"   Published: {'✅ Yes' if iteration.publish_name else '❌ No'}")
            
            if iteration.publish_name:
                print(f"   📢 Published Name: {iteration.publish_name}")
                
                # Try to get performance metrics
                try:
                    performance = trainer.get_iteration_performance(project_id, iteration.id)
                    if performance.overall_precision is not None:
                        print(f"   📊 Precision: {performance.overall_precision:.2%}")
                        print(f"   📊 Recall: {performance.overall_recall:.2%}")
                        print(f"   📊 mAP: {performance.overall_map:.2%}")
                except Exception as e:
                    print(f"   📊 Performance: Not available")
            print()
        
        # Get tags
        print("🏷️ AVAILABLE TAGS:")
        print("-" * 40)
        tags = trainer.get_tags(project_id)
        for tag in tags:
            print(f"• {tag.name} (ID: {tag.id}) - {tag.image_count} images")
        print()
        
        # Get current published iteration details
        published_iterations = [it for it in iterations if it.publish_name]
        if published_iterations:
            print("📢 CURRENTLY PUBLISHED ITERATIONS:")
            print("-" * 40)
            for iteration in published_iterations:
                print(f"✅ {iteration.name}")
                print(f"   Published as: {iteration.publish_name}")
                print(f"   Resource: {iteration.reserved_budget_in_hours}")
                print()
        else:
            print("❌ No published iterations found!")
            
        # Check prediction endpoint access
        print("🔗 ENDPOINT INFORMATION:")
        print("-" * 40)
        print(f"Training Endpoint: {endpoint}")
        prediction_endpoint = os.getenv('PREDICTION_ENDPOINT')
        if prediction_endpoint:
            print(f"Prediction Endpoint: {prediction_endpoint}")
        print()
        
        # Current configuration summary
        published_name = os.getenv('PUBLISHED_NAME')
        print("⚙️ CURRENT CONFIGURATION:")
        print("-" * 40)
        print(f"Project ID: {project_id}")
        print(f"Published Name (configured): {published_name}")
        
        # Verify if configured published name exists
        if published_name:
            matching_iterations = [it for it in published_iterations if it.publish_name == published_name]
            if matching_iterations:
                print(f"✅ Published name '{published_name}' exists and is valid")
            else:
                print(f"❌ Published name '{published_name}' not found!")
                print("Available published names:")
                for it in published_iterations:
                    print(f"   • {it.publish_name}")
        
    except Exception as e:
        print(f"❌ Error checking project details: {str(e)}")
        print("This could be due to:")
        print("• Invalid training key or endpoint")
        print("• Incorrect project ID")
        print("• Network connectivity issues")

if __name__ == "__main__":
    check_project_details()