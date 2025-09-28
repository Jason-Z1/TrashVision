"""
Simple script to check Azure Custom Vision project names and IDs
"""
import os
from dotenv import load_dotenv
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from msrest.authentication import ApiKeyCredentials
from pathlib import Path

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def check_project_info():
    """Check basic project information and published iterations"""
    
    # Get credentials from environment
    training_key = os.getenv('TRAINING_KEY')
    endpoint = os.getenv('ENDPOINT')
    project_id = os.getenv('PROJECT_ID')
    
    if not all([training_key, endpoint, project_id]):
        print("❌ Missing required environment variables!")
        print(f"Training Key: {'✅' if training_key else '❌'}")
        print(f"Endpoint: {'✅' if endpoint else '❌'}")
        print(f"Project ID: {'✅' if project_id else '❌'}")
        return
    
    try:
        # Initialize training client
        credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
        trainer = CustomVisionTrainingClient(endpoint, credentials)
        
        print("=" * 60)
        print("🔍 AZURE CUSTOM VISION PROJECT INFO")
        print("=" * 60)
        
        # Get project information
        project = trainer.get_project(project_id)
        print(f"📋 Project Name: {project.name}")
        print(f"🆔 Project ID: {project.id}")
        print(f"📝 Description: {project.description if project.description else 'No description'}")
        print(f"📅 Created: {project.created}")
        print()
        
        # Get all iterations
        print("🔄 ALL ITERATIONS:")
        print("-" * 40)
        iterations = trainer.get_iterations(project_id)
        
        if not iterations:
            print("❌ No iterations found!")
            return
            
        published_count = 0
        for i, iteration in enumerate(iterations, 1):
            status_icon = "✅" if iteration.status == "Completed" else "🔄"
            print(f"{i}. {status_icon} {iteration.name}")
            print(f"   ID: {iteration.id}")
            print(f"   Status: {iteration.status}")
            print(f"   Created: {iteration.created}")
            
            if iteration.publish_name:
                print(f"   📢 PUBLISHED AS: {iteration.publish_name}")
                published_count += 1
            else:
                print(f"   📢 Published: No")
            print()
        
        print(f"📊 Summary: {len(iterations)} total iterations, {published_count} published")
        print()
        
        # Current configuration check
        configured_name = os.getenv('PUBLISHED_NAME', os.getenv('PREDICTION_PUBLISHED_NAME'))
        print("⚙️ CURRENT CONFIGURATION:")
        print("-" * 40)
        print(f"Project ID: {project_id}")
        print(f"Configured Published Name: {configured_name}")
        
        # Verify configuration
        published_iterations = [it for it in iterations if it.publish_name]
        if configured_name and published_iterations:
            matching = [it for it in published_iterations if it.publish_name == configured_name]
            if matching:
                print(f"✅ Configuration is VALID - '{configured_name}' exists")
            else:
                print(f"❌ Configuration ISSUE - '{configured_name}' not found!")
                print("Available published names:")
                for it in published_iterations:
                    print(f"   • {it.publish_name}")
        
        # Endpoint information
        print()
        print("🔗 ENDPOINT CONFIGURATION:")
        print("-" * 40)
        print(f"Training Endpoint: {endpoint}")
        prediction_endpoint = os.getenv('PREDICTION_ENDPOINT')
        if prediction_endpoint:
            print(f"Prediction Endpoint: {prediction_endpoint}")
        else:
            print("Prediction Endpoint: Not configured")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    check_project_info()