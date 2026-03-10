# ⚙️ Backend — Health Impact Analyzer API

FastAPI Python backend providing health prediction and report generation.

## Structure
```
backend/
├── main.py              # FastAPI app & all endpoints
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
└── tools/
    ├── prediction/      # health_impact_predictor.py — AI risk scoring
    ├── report_generation/ # medical_report_generator.py, pdf_compiler.py
    ├── visualization/   # health_dashboard_creator.py — risk charts
    ├── intervention/    # schedule_generator.py — 90-day plan
    ├── communication/   # email_delivery.py
    └── data_management/ # google_sheets_logger.py
```

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/predict` | AI health risk prediction |
| POST | `/api/report/clinical` | Generate clinical PDF |
| POST | `/api/report/visualization` | Generate visual risk report |
| POST | `/api/report/schedule` | Generate 90-day Excel schedule |
| GET | `/health` | Health check |

## Run
```bash
pip install -r requirements.txt
cp .env.example .env   # Fill in your API keys
python main.py         # http://localhost:8000
```

## Dependencies
- FastAPI + Uvicorn
- LiteLLM (AI model abstraction)
- ReportLab (PDF generation)
- OpenPyXL (Excel generation)
- Google API client
