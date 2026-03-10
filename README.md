# 🧬 Health Impact Analyzer

AI-powered health risk assessment & personalized intervention planning system.

## 📁 Project Structure

```
Impact Analyzer/
├── frontend/               # React + Vite frontend (Health Impact Predictor UI)
│   └── life-impact-planner/
│       ├── src/
│       │   ├── pages/      # Assessment, Dashboard, Index, NotFound
│       │   ├── components/ # UI components (shadcn/ui)
│       │   └── hooks/
│       └── package.json
│
├── backend/                # FastAPI Python backend
│   ├── main.py             # API server (FastAPI + all routes)
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variable template
│   └── tools/
│       ├── prediction/     # AI health risk prediction
│       ├── report_generation/ # PDF/clinical report generation
│       ├── visualization/  # Risk chart & dashboard creation
│       ├── intervention/   # 90-day schedule generator
│       ├── communication/  # Email delivery
│       └── data_management/ # Google Sheets logger
│
├── database/               # Database config & migrations
│   └── supabase/           # Supabase config (config.toml)
│
├── scripts/                # Utility & setup scripts
│   └── authenticate_gmail.py  # Gmail OAuth setup script
│
└── docs/                   # Documentation
```

## 🚀 Quick Start

### Frontend
```bash
cd frontend/life-impact-planner
npm install
npm run dev
# Runs at http://localhost:8080
```

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env    # Add your API keys
python main.py
# Runs at http://localhost:8000
```

## 🔑 Environment Variables
See `backend/.env.example`:
- `GROQ_API_KEY` — Groq LLM API key
- `GEMINI_API_KEY` — Google Gemini API key  
- `GOOGLE_SHEET_ID` — Google Sheets ID for data logging

## 🌐 Live Site
https://antigravity-health.vercel.app/
