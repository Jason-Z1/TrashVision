"""
Upload images from backend/data/Recyclable and backend/data/Non-recyclable to Azure Custom Vision,
train the project, and optionally publish the iteration.

Usage (PowerShell):
$env:AZURE_CUSTOM_VISION_TRAINING_ENDPOINT = '<training-endpoint>'
$env:AZURE_CUSTOM_VISION_TRAINING_KEY = '<training-key>'
# Optional: provide prediction resource id to publish
$env:AZURE_CUSTOM_VISION_PREDICTION_RESOURCE_ID = '<prediction-resource-id>'
python backend/scripts/train_custom_vision.py --project-name TrashVision --publish-name trashvision-v1

Places to put images:
- backend/data/Recyclable/*.jpg
- backend/data/Non-recyclable/*.jpg

This script uses the Azure Custom Vision Training SDK (azure-cognitiveservices-vision-customvision).
"""
import os
import sys
import time
from pathlib import Path
from typing import List

try:
    from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
    from msrest.authentication import ApiKeyCredentials
    from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateEntry, ImageFileCreateBatch
except Exception as e:
    print("Missing Azure Custom Vision training SDK. Install requirements: 'pip install azure-cognitiveservices-vision-customvision msrest'")
    raise


def collect_images(folder: Path) -> List[ImageFileCreateEntry]:
    entries = []
    for f in folder.glob('*'):
        if f.is_file():
            with open(f, 'rb') as fh:
                data = fh.read()
            entries.append(ImageFileCreateEntry(name=f.name, contents=data))
    return entries


def main():
    endpoint = os.getenv('AZURE_CUSTOM_VISION_TRAINING_ENDPOINT')
    key = os.getenv('AZURE_CUSTOM_VISION_TRAINING_KEY')
    prediction_resource_id = os.getenv('AZURE_CUSTOM_VISION_PREDICTION_RESOURCE_ID')

    if not endpoint or not key:
        print('Please set AZURE_CUSTOM_VISION_TRAINING_ENDPOINT and AZURE_CUSTOM_VISION_TRAINING_KEY in the environment.')
        sys.exit(1)

    creds = ApiKeyCredentials(in_headers={'Training-key': key})
    trainer = CustomVisionTrainingClient(endpoint, creds)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-name', default='TrashVision')
    parser.add_argument('--publish-name', default='trashvision-v1')
    parser.add_argument('--data-dir', default=os.path.join('backend', 'data'))
    args = parser.parse_args()

    # Find or create project
    projects = trainer.get_projects()
    project = None
    for p in projects:
        if p.name == args.project_name:
            project = p
            break
    if not project:
        print(f'Creating project {args.project_name}')
        project = trainer.create_project(args.project_name)
    else:
        print(f'Using existing project {project.name} ({project.id})')

    # Ensure tags exist
    recyclable_tag = None
    nonrecyc_tag = None
    tags = trainer.get_tags(project.id)
    for t in tags:
        if t.name.lower() == 'recyclable':
            recyclable_tag = t
        if t.name.lower() == 'non-recyclable' or t.name.lower() == 'non recyclable' or t.name.lower() == 'nonrecyclable':
            nonrecyc_tag = t

    if not recyclable_tag:
        recyclable_tag = trainer.create_tag(project.id, 'Recyclable')
        print('Created tag Recyclable')
    if not nonrecyc_tag:
        nonrecyc_tag = trainer.create_tag(project.id, 'Non-recyclable')
        print('Created tag Non-recyclable')

    data_dir = Path(args.data_dir)
    recyclable_dir = data_dir / 'Recyclable'
    nonrecyc_dir = data_dir / 'Non-recyclable'

    if not recyclable_dir.exists() or not nonrecyc_dir.exists():
        print('Data directories not found. Please create:')
        print(str(recyclable_dir.resolve()))
        print(str(nonrecyc_dir.resolve()))
        sys.exit(1)

    # Upload images for Recyclable
    print('Collecting Recyclable images...')
    rec_entries = collect_images(recyclable_dir)
    print(f'Found {len(rec_entries)} files')
    if rec_entries:
        # Tag each entry with recyclable_tag id
        batch_entries = []
        for e in rec_entries:
            e.tag_ids = [recyclable_tag.id]
            batch_entries.append(e)
        print('Uploading Recyclable images...')
        # API supports batching but limit may apply; we'll upload in batches of 64
        BATCH = 64
        for i in range(0, len(batch_entries), BATCH):
            batch = batch_entries[i:i+BATCH]
            images = ImageFileCreateBatch(images=batch)
            upload_result = trainer.create_images_from_files(project.id, images)
            if not upload_result.is_batch_successful:
                print('Some images failed to upload in Recyclable batch:', upload_result)

    # Upload images for Non-recyclable
    print('Collecting Non-recyclable images...')
    non_entries = collect_images(nonrecyc_dir)
    print(f'Found {len(non_entries)} files')
    if non_entries:
        batch_entries = []
        for e in non_entries:
            e.tag_ids = [nonrecyc_tag.id]
            batch_entries.append(e)
        print('Uploading Non-recyclable images...')
        BATCH = 64
        for i in range(0, len(batch_entries), BATCH):
            batch = batch_entries[i:i+BATCH]
            images = ImageFileCreateBatch(images=batch)
            upload_result = trainer.create_images_from_files(project.id, images)
            if not upload_result.is_batch_successful:
                print('Some images failed to upload in Non-recyclable batch:', upload_result)

    # Train
    print('Training project...')
    iteration = trainer.train_project(project.id)
    # Wait for training to complete (the SDK may return when training is done but we poll status)
    while iteration.status != 'Completed':
        print('Training status:', iteration.status)
        time.sleep(2)
        iteration = trainer.get_iteration(project.id, iteration.id)
    print('Training completed. Iteration id:', iteration.id)

    # Publish iteration if prediction resource id provided
    publish_name = args.publish_name
    if prediction_resource_id:
        print('Publishing iteration...')
        trainer.publish_iteration(project.id, iteration.id, publish_name, prediction_resource_id)
        print(f'Published iteration as {publish_name}')
    else:
        print('No prediction resource id provided; skipping publish. You can publish the iteration in the portal or provide AZURE_CUSTOM_VISION_PREDICTION_RESOURCE_ID env var.')

    print('Done. Project ID:', project.id)
    print('Use the project ID and publish name in the backend env vars:')
    print('AZURE_CUSTOM_VISION_PROJECT_ID=', project.id)
    print('AZURE_CUSTOM_VISION_PUBLISHED_NAME=', publish_name)


if __name__ == '__main__':
    main()
