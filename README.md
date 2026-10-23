# Chargebee Subscription Billing Dashboard

A full-stack portfolio project that combines a React frontend with a Flask backend to connect to the Chargebee test environment securely.

## Features
- Dashboard with summary cards
- Customer listing with pagination and search
- Subscription tracking with filter and trial status
- Invoice overview and details
- Subscription creation using Chargebee test data
- Secure backend-only environment variables
- Loading, empty, and error states
- Backend unit tests

## Tech stack
- Frontend: React + Vite + JavaScript + CSS
- Backend: Flask + Python 3.11+
- Billing API: Chargebee Python SDK
- Data: SQLite (local persistence for project records)

## Project structure
```text
chargebee-billing-dashboard/
├── backend/
│   ├── app.py
│   ├── chargebee_service.py
│   ├── config.py
│   ├── database.py
│   ├── requirements.txt
│   ├── .env.example
│   └── tests/
│       └── test_app.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── styles.css
│       └── services/
│           └── api.js
├── .gitignore
├── README.md
└── .github/ (optional, if later added)
```

## Environment setup

1. Create the backend environment file:
```bash
cd backend
copy .env.example .env
```
Then update `.env` with your Chargebee test details:
```env
CHARGEBEE_API_KEY=your_test_api_key
CHARGEBEE_SITE=your_test_site
DEMO_MODE=true
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
ALLOWED_ORIGINS=http://localhost:5173
```

2. Create the frontend env file:
```bash
cd frontend
copy .env.example .env
```
Example:
```env
VITE_API_URL=http://localhost:5001
```

## Install and run backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Install and run frontend
Open a second terminal:
```bash
cd frontend
npm install
npm run dev
```

Then open:
```text
http://localhost:5173
```

## Backend endpoints
- `GET /api/health`
- `GET /api/chargebee/test-connection`
- `GET /api/dashboard`
- `GET /api/customers`
- `GET /api/subscriptions`
- `GET /api/subscriptions/<subscription_id>`
- `POST /api/subscriptions`
- `GET /api/invoices`
- `GET /api/invoices/<invoice_id>`

## Testing
```bash
cd backend
python -m unittest discover -s tests -v
```

## Notes
- Use only Chargebee test-site credentials.
- Never commit real secrets.
- If Chargebee keys are missing, the app runs in demo mode with sample data to keep local development safe and functional.
- For production deployment, add your environment variables in the hosting platform and disable demo mode.

## GitHub publishing
```bash
git init
git add .
git commit -m "Initial commit: Chargebee billing dashboard"
git branch -M main
git remote add origin https://github.com/<your-username>/chargebee-billing-dashboard.git
git push -u origin main
```

## Deploy to Render

The root `render.yaml` defines a Render Blueprint with a Flask API and a Vite static site. Connect the GitHub repository in Render and choose **New + → Blueprint**. Render builds and deploys both services, wiring the frontend API URL and backend CORS origin automatically.

The deployment starts in demo mode and does not require billing credentials. To connect a Chargebee test site after deployment, add `CHARGEBEE_API_KEY` and `CHARGEBEE_SITE` as secret environment variables on the API service, then set `DEMO_MODE=false`. Never put these values in source control or in the frontend environment.

## Portfolio description
This project demonstrates a complete full-stack billing dashboard using React, Flask, and the Chargebee API. It includes dashboard metrics, customer and subscription management, invoice handling, secure environment configuration, responsive design, and careful error handling. It is a polished portfolio project showing practical billing workflows and API integration skills.
