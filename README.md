# THRYVE — RoadGuard AI

A Streamlit prototype for AI-assisted pothole and road-distress reporting, review, mapping, and CSV export.

## Features
- Road-hazard dashboard with severity and review metrics
- Upload and preview road images
- Optional Ultralytics YOLO inference when compatible weights are supplied
- Manual hazard reports with coordinates
- Map view and searchable/filterable report table
- CSV export for filtered or all reports

## Requirements
- Python 3.10–3.12 recommended
- Internet connection for package installation and map tiles

## Run locally

```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

macOS/Linux:
```bash
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Enable optional AI inference
Create a `models/` directory and place compatible pothole-trained Ultralytics weights at `models/pothole_model.pt`. The app does not include model weights. A generic YOLO model is not necessarily a pothole detector; verify the model's classes, license, and performance before use.

## Prototype limitations
- Reports are stored in Streamlit session state, not a persistent database.
- Included sample records and coordinates are illustrative; replace them with verified reports.
- Severity is an estimate and must be confirmed by a human reviewer.
- Do not use this prototype as the sole basis for safety or road-repair decisions.
