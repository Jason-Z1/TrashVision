"""
Upload images from backend/data/Recyclable and backend/data/Nonrecyclable to Azure Custom Vision,
train the project, and optionally publish the iteration.

Usage (PowerShell):
$env:ENDPOINT = '<training-endpoint>'
$env:TRAINING_KEY = '<training-key>'
# Optional: provide prediction resource id to publish
$env:PREDICTION_RESOURCE_ID = '<prediction-resource-id>'
python backend/scripts/train_custom_vision.py --project-name TrashVision --publish-name trashvision-v3

Places to put images:
- backend/data/Recyclable/*.jpg
- backend/data/Nonrecyclable/*.jpg

This script uses the Azure Custom Vision Training SDK (azure-cognitiveservices-vision-customvision).
"""
import os
import sys
import time
import requests
from dotenv import load_dotenv
from pathlib import Path
from typing import List

env_path = Path(__file__).resolve().parent.parent / ".env"
print("Looking for .env at:", env_path)
load_dotenv(dotenv_path=env_path)


print("Testing endpoint connectivity...")
print(requests.get(os.getenv("ENDPOINT")).status_code)
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


print("ENDPOINT from env:", os.getenv("ENDPOINT"))
print("TRAINING_KEY from env:", os.getenv("TRAINING_KEY"))
print("PREDICTION_RESOURCE_ID from env:", os.getenv("PREDICTION_RESOURCE_ID"))


def main():
    endpoint = os.getenv('ENDPOINT')
    key = os.getenv('TRAINING_KEY')
    prediction_resource_id = os.getenv('PREDICTION_RESOURCE_ID')

    if not endpoint or not key:
        print('Please set ENDPOINT and TRAINING_KEY in the environment.')
        sys.exit(1)

    creds = ApiKeyCredentials(in_headers={'Training-key': key})
    trainer = CustomVisionTrainingClient(endpoint, creds)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-name', default='RecycleSmart')
    parser.add_argument('--publish-name', default='trashvision-v3')
    parser.add_argument('--dry-run', action='store_true', help='List files and tags that would be uploaded without calling the API')
    parser.add_argument('--min-images', type=int, default=8, help='Minimum images required per recyclable subfolder to include it in training')
    parser.add_argument('--batch-size', type=int, default=64, help='Number of images to send per upload batch')

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

    # Auto-detect folder layout under data_dir and follow priority:
    # 1) If Recyclable/ contains subfolders with images, process those per-item tags.
    # 2) Else, if Nonrecyclable/ contains subfolders, process those per-item tags.
    # 3) Else, if Nonrecyclable/ contains files, upload them under a single Nonrecyclable tag.
    # 4) Else, fallback: collect any images under data_dir and tag as Nonrecyclable.
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print('Data directory not found. Expected structure:')
        print(str(data_dir.resolve()))
        sys.exit(1)

    recyclable_dir = data_dir / 'Recyclable'
    nonrecyc_dir = data_dir / 'Nonrecyclable'

    # Debug: print resolved paths and immediate subfolders to ensure we're scanning the right location
    try:
        print('Resolved data_dir:', str(data_dir.resolve()))
    except Exception:
        print('Resolved data_dir: <unable to resolve>')
    print('Looking for recyclable_dir at:', str(recyclable_dir))
    print('Looking for nonrecyc_dir at:', str(nonrecyc_dir))
    top_folders = [p for p in data_dir.iterdir() if p.is_dir()]
    print('Immediate subfolders under data_dir:', [p.name for p in top_folders])

    # Get existing tags once (map by lowercase name)
    existing_tags = {t.name.lower(): t for t in trainer.get_tags(project.id)}

    # --- Clean up old tags not present in current folders ---
    current_tag_names = [p.name.lower() for p in recyclable_dir.iterdir() if p.is_dir()] + ['nonrecyclable']
    for t in list(existing_tags.values()):
        if t.name.lower() not in current_tag_names:
            print(f"Deleting old tag: {t.name}")
            try:
                trainer.delete_tag(project.id, t.id)
                del existing_tags[t.name.lower()]
            except Exception as e:
                print(f"  Could not delete tag {t.name}: {e}")


    material_tags = {}
    handled_nonrecyclable = False

    def count_files(folder: Path) -> int:
        return sum(1 for f in folder.iterdir() if f.is_file())

    # 1) Prefer Recyclable subfolders if present and meet min_images
    recyclable_material_dirs = []
    if recyclable_dir.exists():
        for p in recyclable_dir.iterdir():
            if p.is_dir():
                if count_files(p) >= args.min_images:
                    recyclable_material_dirs.append(p)
                else:
                    print(f'Found recyclable subfolder {p.name} but only {count_files(p)} files (< {args.min_images}); will skip')

    if recyclable_material_dirs:
        print('Processing recyclable subfolders:')
        for mdir in recyclable_material_dirs:
            tag_name = mdir.name
            tag = existing_tags.get(tag_name.lower())
            if not tag:
                tag = trainer.create_tag(project.id, tag_name)
                print(f'Created tag for recyclable item: {tag_name}')
            else:
                print(f'Using existing tag for recyclable item: {tag_name}')
            material_tags[mdir] = tag
    else:
        # 2) No recyclable subfolders found (or none with enough images) -> try Nonrecyclable
        if nonrecyc_dir.exists():
            non_subfolders = [p for p in nonrecyc_dir.iterdir() if p.is_dir() and count_files(p) >= args.min_images]
            if non_subfolders:
                print('No recyclable categories found; processing Nonrecyclable subfolders as tags:')
                for mdir in non_subfolders:
                    tag_name = mdir.name
                    tag = existing_tags.get(tag_name.lower())
                    if not tag:
                        tag = trainer.create_tag(project.id, tag_name)
                        print(f'Created tag for nonrecyclable item: {tag_name}')
                    else:
                        print(f'Using existing tag for nonrecyclable item: {tag_name}')
                    material_tags[mdir] = tag
                handled_nonrecyclable = True
            else:
                # 3) No nonrecyclable subfolders with enough images; if there are files directly under Nonrecyclable, upload them under single tag
                direct_files = []
                if nonrecyc_dir.exists():
                    direct_files = [f for f in nonrecyc_dir.iterdir() if f.is_file()]
                if direct_files:
                    print('No recyclable categories found and no nonrecyclable subcategories; will upload direct Nonrecyclable files under single tag')
                    # ensure tag exists
                    nonrecyc_tag = existing_tags.get('nonrecyclable')
                    if not nonrecyc_tag:
                        nonrecyc_tag = trainer.create_tag(project.id, 'Nonrecyclable')
                        print('Created tag Nonrecyclable')
                    material_tags[nonrecyc_dir] = nonrecyc_tag
                    handled_nonrecyclable = True
                else:
                    # 4) Fallback: collect any images under data_dir recursively and upload under Nonrecyclable
                    print('No recyclable or nonrecyclable images found in standard locations; falling back to scanning all folders and tagging as Nonrecyclable')
                    # create Nonrecyclable tag if needed
                    nonrecyc_tag = existing_tags.get('nonrecyclable')
                    if not nonrecyc_tag:
                        nonrecyc_tag = trainer.create_tag(project.id, 'Nonrecyclable')
                        print('Created tag Nonrecyclable')
                    # create a virtual 'all_data' entry representing the folder
                    material_tags[data_dir] = nonrecyc_tag
                    handled_nonrecyclable = True

    BATCH = args.batch_size
    # Upload images per material tag
    for mdir, tag in material_tags.items():
        entries = collect_images(mdir)
        print(f'Found {len(entries)} images for recyclable item {mdir.name} (min required: {args.min_images})')
        if len(entries) < args.min_images:
            print(f'  Skipping {mdir.name}: only {len(entries)} images (below min {args.min_images})')
            continue
        batch_entries = []
        for e in entries:
            e.tag_ids = [tag.id]
            batch_entries.append(e)
        if args.dry_run:
            print(f'  Dry-run: would upload {len(batch_entries)} images for {mdir.name} with tag id {tag.id}')
            # print sample filenames
            sample = [b.name for b in batch_entries[:5]]
            print('   Sample files:', sample)
            continue
        print(f'Uploading images for recyclable item {mdir.name} in batches of {BATCH}...')
        for i in range(0, len(batch_entries), BATCH):
            batch = batch_entries[i:i+BATCH]
            images = ImageFileCreateBatch(images=batch)
            upload_result = trainer.create_images_from_files(project.id, images)
            # upload_result contains per-image status; print detailed info on failures
            if not upload_result.is_batch_successful:
                print(f'  Some images failed to upload in batch for {mdir.name}:')
                for img_result in upload_result.images:
                    if img_result.status != "OK":
                        print(f"Failed image: {img_result.source_url}, status: {img_result.status}")

    # --- Nonrecyclable: collect all images under Nonrecyclable/* and tag them as a single Nonrecyclable tag ---
    nonrecyc_tag = existing_tags.get('nonrecyclable')
    if not nonrecyc_tag:
        nonrecyc_tag = trainer.create_tag(project.id, 'Nonrecyclable')
        print('Created tag Nonrecyclable')

    non_entries = []
    if nonrecyc_dir.exists():
        for p in nonrecyc_dir.iterdir():
            if p.is_dir():
                non_entries.extend(collect_images(p))
            elif p.is_file():
                # also include files directly under Nonrecyclable/
                non_entries.extend(collect_images(nonrecyc_dir))
                break
    else:
        print('Warning: Nonrecyclable directory not found at', nonrecyc_dir)

    print(f'Found {len(non_entries)} nonrecyclable images')
    if non_entries:
        batch_entries = []
        for e in non_entries:
            e.tag_ids = [nonrecyc_tag.id]
            batch_entries.append(e)
        if args.dry_run:
            print(f'  Dry-run: would upload {len(batch_entries)} nonrecyclable images with tag id {nonrecyc_tag.id}')
        else:
            print('Uploading Nonrecyclable images in batches of', BATCH)
            for i in range(0, len(batch_entries), BATCH):
                batch = batch_entries[i:i+BATCH]
                images = ImageFileCreateBatch(images=batch)
                upload_result = trainer.create_images_from_files(project.id, images)
                if not upload_result.is_batch_successful:
                    print('  Some images failed to upload in Nonrecyclable batch:')
                    for img_result in getattr(upload_result, 'images', []):
                        if not getattr(img_result, 'status', True):
                            print('    Failed:', getattr(img_result, 'source_picture', getattr(img_result, 'image', getattr(img_result, 'file_name', '<unknown>'))))


    # Train
    print('Training project...')
    tags = trainer.get_tags(project.id)
    for t in tags:
        images = trainer.get_tagged_images(project.id, tag_ids=[t.id])
        print(t.name, "->", len(images))

    try:
        iteration = trainer.train_project(project.id)
    except Exception as e:
        if "Nothing changed" in str(e):
            print("No new images or tags since last training; skipping training.")
        # Optionally, fetch the last iteration instead
        iterations = trainer.get_iterations(project.id)
        iteration = iterations[-1]  # get the most recent iteration
        raise  # re-raise unexpected errors

    print("Iteration ID:", iteration.id)
    print("Iteration status:", iteration.status)

    # Wait for training to complete (the SDK may return when training is done but we poll status)
    while iteration.status != 'Completed':
        print('Training status:', iteration.status)
        time.sleep(2)
        iteration = trainer.get_iteration(project.id, iteration.id)
    print('Training completed. Iteration id:', iteration.id)

    # Publish iteration if prediction resource id provided
    publish_name = args.publish_name
    print(publish_name)
    if prediction_resource_id:
        print('Publishing iteration...')
        trainer.publish_iteration(project.id, iteration.id, publish_name, prediction_resource_id)
        print(f'Published iteration as {publish_name}')
    else:
        print('No prediction resource id provided; skipping publish. You can publish the iteration in the portal or provide AZURE_CUSTOM_VISION_PREDICTION_RESOURCE_ID env var.')

    print('Done. Project ID:', project.id)
    print('Use the project ID and publish name in the backend env vars:')
    print('PROJECT_ID=', project.id)
    print('TRAINING_PUBLISHED_NAME=', publish_name)


if __name__ == '__main__':
    main()
