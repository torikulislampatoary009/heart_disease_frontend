# Heart Disease Diagnostic Tool - frontend (Python / Flask)

Server-rendered pages: check form, result, history, and a "how it works" page with the test results.
It talks to the backend only through its URL.

## Deploy on Render (free)
1. Push to GitHub. New Web Service -> same repo -> Root Directory `frontend`.
2. Build: `pip install -r requirements.txt`
   Start: `gunicorn app:app --workers 1 --threads 2 --timeout 120 --bind 0.0.0.0:$PORT`
3. Environment variables:
   - `BACKEND_URL` = your backend's Render URL, no trailing slash
   - `SECRET_KEY` = any long random text
   - `PYTHON_VERSION` = 3.11.9

## Local run
    pip install -r requirements.txt
    set BACKEND_URL=http://localhost:5000      (Mac/Linux: export ...)
    python app.py        # opens on http://localhost:8000

The first request after the backend sleeps can take up to a minute on Render's free plan.
