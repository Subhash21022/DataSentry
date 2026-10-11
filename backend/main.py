import io
import json
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import pandas as pd
from jinja2 import Template

from datasentry.core.profiler import DataProfiler
from datasentry.core.validator import DataValidator
from datasentry.core.ml_anomaly import MLAnomalyDetector
from datasentry.core.reporter import HTML_TEMPLATE

app = FastAPI(
    title="DataSentry API",
    description="Backend API for DataSentry: All-in-One Data Quality, Profiling & ML Anomaly Detection Platform",
    version="0.1.0",
)

# Enable CORS for React Frontend (typically running on localhost:5173 or localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "DataSentry Unified Engine",
        "version": "0.1.0",
    }


def parse_csv_upload(file_bytes: bytes) -> pd.DataFrame:
    try:
        return pd.read_csv(io.BytesIO(file_bytes))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV file: {str(e)}")


@app.post("/api/profile")
async def profile_dataset(file: UploadFile = File(...)):
    """
    Upload a CSV file and receive complete statistical and semantic profiling.
    """
    content = await file.read()
    df = parse_csv_upload(content)
    profiler = DataProfiler(df)
    report = profiler.run_profile()
    return report


@app.post("/api/validate")
async def validate_dataset(
    file: UploadFile = File(...),
    rules_json: Optional[str] = Form(None),
):
    """
    Upload a CSV file and execute deterministic validation rules.
    """
    content = await file.read()
    df = parse_csv_upload(content)

    rules = []
    if rules_json:
        try:
            parsed = json.loads(rules_json)
            rules = parsed.get("rules", parsed if isinstance(parsed, list) else [])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid rules JSON: {str(e)}")

    validator = DataValidator(df, rules)
    result = validator.validate()
    return result


@app.post("/api/anomalies")
async def detect_anomalies(
    file: UploadFile = File(...),
    contamination: float = Form(0.05),
):
    """
    Upload a CSV file and detect multivariate tabular anomalies via Scikit-Learn Isolation Forest.
    """
    content = await file.read()
    df = parse_csv_upload(content)
    detector = MLAnomalyDetector(df, contamination=contamination)
    result = detector.detect_anomalies()
    return result


@app.post("/api/report/html", response_class=HTMLResponse)
async def generate_html(file: UploadFile = File(...)):
    """
    Upload a CSV file and receive an interactive standalone HTML report.
    """
    content = await file.read()
    df = parse_csv_upload(content)
    profiler = DataProfiler(df)
    profile_data = profiler.run_profile()
    template = Template(HTML_TEMPLATE)
    return template.render(profile=profile_data)
