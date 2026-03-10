# 🖥️ Frontend — Health Impact Predictor

React + Vite + TypeScript + shadcn/ui frontend.

## Structure
```
life-impact-planner/
├── src/
│   ├── pages/
│   │   ├── Assessment.tsx   # 5-step health assessment wizard
│   │   ├── Dashboard.tsx    # Results & report downloads
│   │   ├── Index.tsx        # Landing page (unused in Vercel deploy)
│   │   └── NotFound.tsx
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   └── ChatInterface.tsx
│   ├── hooks/
│   ├── lib/
│   └── integrations/supabase/
├── package.json
└── vite.config.ts
```

## Run
```bash
cd life-impact-planner
npm install
npm run dev    # http://localhost:8080
npm run build  # Production build
```

## Tech Stack
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS + shadcn/ui
- React Router DOM
- TanStack Query
