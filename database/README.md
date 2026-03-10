# 🗄️ Database — Supabase Config

Supabase is used for authentication and data persistence.

## Structure
```
database/
└── supabase/
    └── config.toml     # Supabase local dev config
```

## Setup
1. Install Supabase CLI: `npm install -g supabase`
2. Login: `supabase login`
3. Link project: `supabase link --project-ref <your-project-ref>`
4. Start local: `supabase start`

## Environment Variables
Add to `backend/.env`:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
GOOGLE_SHEET_ID=your-google-sheet-id
```

## Google Sheets (Data Logging)
Patient assessment data can be logged to Google Sheets via `backend/tools/data_management/google_sheets_logger.py`.
Set `GOOGLE_SHEET_ID` in your `.env` file.
