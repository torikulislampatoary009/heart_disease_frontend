import os

import requests
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000").rstrip("/")
TIMEOUT = 90   # Render free backends can take ~50 s to wake up

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-me-in-render-env")

YESNO = [(1, "Yes"), (0, "No")]
FIELDS = [
    {"name": "age", "label": "Age", "hint": "years", "type": "number", "min": 1, "max": 120, "step": 1},
    {"name": "sex", "label": "Sex", "options": [(1, "Male"), (0, "Female")]},
    {"name": "cp", "label": "Chest pain type", "options": [
        (1, "Typical angina"), (2, "Atypical angina"), (3, "Non-anginal pain"), (4, "No symptoms (asymptomatic)")]},
    {"name": "trestbps", "label": "Resting blood pressure", "hint": "mm Hg", "type": "number", "min": 60, "max": 260, "step": 1},
    {"name": "chol", "label": "Cholesterol", "hint": "mg/dl", "type": "number", "min": 80, "max": 700, "step": 1},
    {"name": "fbs", "label": "Fasting blood sugar above 120 mg/dl", "options": YESNO},
    {"name": "restecg", "label": "Resting ECG result", "options": [
        (0, "Normal"), (1, "ST-T wave abnormality"), (2, "Left ventricular hypertrophy")]},
    {"name": "thalach", "label": "Highest heart rate reached", "hint": "beats per minute", "type": "number", "min": 50, "max": 250, "step": 1},
    {"name": "exang", "label": "Chest pain during exercise", "options": YESNO},
    {"name": "oldpeak", "label": "ST depression after exercise", "hint": "0 to 10", "type": "number", "min": 0, "max": 10, "step": 0.1},
    {"name": "slope", "label": "Slope of the ST segment at peak exercise", "options": [
        (1, "Upsloping"), (2, "Flat"), (3, "Downsloping")]},
    {"name": "ca", "label": "Major vessels colored by fluoroscopy", "options": [(0, "0"), (1, "1"), (2, "2"), (3, "3")]},
    {"name": "thal", "label": "Thallium stress test", "options": [
        (3, "Normal"), (6, "Fixed defect"), (7, "Reversible defect")]},
]


def call_api(method, path, **kw):
    """Returns (data, error_message)."""
    try:
        r = requests.request(method, BACKEND_URL + path, timeout=TIMEOUT, **kw)
        data = r.json() if r.content else {}
        if r.status_code >= 400:
            return None, data.get("error", f"Server returned {r.status_code}")
        return data, None
    except requests.exceptions.Timeout:
        return None, "The server took too long to answer. It may be waking up, so try again in a minute."
    except requests.exceptions.RequestException:
        return None, "Cannot reach the server. Check that BACKEND_URL is correct and the backend is running."


@app.get("/")
def index():
    return render_template("index.html", fields=FIELDS, values={}, error=None)


@app.post("/predict")
def predict():
    values = {f["name"]: request.form.get(f["name"], "").strip() for f in FIELDS}
    payload = dict(values, save=request.form.get("save") == "on")
    data, error = call_api("POST", "/api/predict", json=payload)
    if error:
        return render_template("index.html", fields=FIELDS, values=values, error=error), 400
    return render_template("result.html", r=data, fields=FIELDS)


@app.get("/history")
def history():
    page = max(request.args.get("page", 1, type=int), 1)
    data, error = call_api("GET", "/api/history", params={"page": page, "limit": 10})
    stats, _ = call_api("GET", "/api/stats") if data else (None, None)
    pages = max(1, -(-data["total"] // 10)) if data else 1
    return render_template("history.html", data=data, stats=stats, error=error, page=page, pages=pages)


@app.post("/history/<int:rid>/delete")
def delete(rid):
    _, error = call_api("DELETE", f"/api/history/{rid}")
    if error:
        flash(error)
    return redirect(url_for("history"))


@app.get("/model")
def model():
    data, error = call_api("GET", "/api/model-info")
    return render_template("model.html", info=data, error=error)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)), debug=False)
