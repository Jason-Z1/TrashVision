# TrashVision Backend (FastAPI)

This backend accepts an image upload at `/predict` and returns:
- `label`: `recyclable` | `non-recyclable` | `unknown`
- `source`: where the label came from (`azure_custom_vision`, `heuristic`, ...)
- `predictions`: array of predictions returned by Azure Custom Vision (if used)
- `description`: caption from Azure Computer Vision Describe (if used)

The backend will call Azure Custom Vision Prediction if environment variables are set. It will also call Azure Computer Vision Describe to produce a human-friendly caption.

## Setup (PowerShell)

```powershell
cd c:\Users\bpatn\OneDrive\Documents\GitHub\TrashVision\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
# from repository root or backend folder
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

## Environment variables (optional for Azure)

- `AZURE_CUSTOM_VISION_ENDPOINT` e.g. `https://<resource>.cognitiveservices.azure.com/`
- `AZURE_CUSTOM_VISION_PREDICTION_KEY`
- `AZURE_CUSTOM_VISION_PROJECT_ID`
- `AZURE_CUSTOM_VISION_PUBLISHED_NAME`
- `AZURE_COMPUTER_VISION_ENDPOINT`
- `AZURE_COMPUTER_VISION_KEY`

Set them in PowerShell before running the server (example):

```powershell
$env:AZURE_CUSTOM_VISION_ENDPOINT = 'https://<your-resource>.cognitiveservices.azure.com/';
$env:AZURE_CUSTOM_VISION_PREDICTION_KEY = '<your-prediction-key>'
$env:AZURE_CUSTOM_VISION_PROJECT_ID = '<your-project-id>'
$env:AZURE_CUSTOM_VISION_PUBLISHED_NAME = '<your-published-iteration-name>'
$env:AZURE_COMPUTER_VISION_ENDPOINT = 'https://<your-resource>.cognitiveservices.azure.com/'
$env:AZURE_COMPUTER_VISION_KEY = '<your-computer-vision-key>'

# Instead of pasting keys into the terminal, copy the example .env file and fill it locally:
# copy .env.example .env

# Run the server (from the repository root):
# uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000

# Or, if you cd into the backend folder, run:
# uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Example response

```json
{
  "label": "recyclable",
  "source": "azure_custom_vision",
  "predictions": [
    {"tag": "plastic_bottle", "probability": 0.93},
    {"tag": "food_waste", "probability": 0.05}
  ],
  "description": "a plastic bottle on a table"
}
```

## Notes

- Do not commit keys to source control. Use a secrets manager for production.
- Customize `map_tag_to_label` to match your Custom Vision tag names for best results.
- For performance, consider loading a local model or hosting inference closer to your clients.
