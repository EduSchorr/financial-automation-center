from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.refund_reconciliation import RefundReconciliationService
from backend.monitoring import MonitoringService

ROOT = Path(__file__).resolve().parent

app = FastAPI(title="Financial Automation Center", version="portfolio")
app.mount("/static", StaticFiles(directory=ROOT / "frontend"), name="static")

refunds = RefundReconciliationService()
monitoring = MonitoringService()

@app.get("/api/health")
def health():
    return {"ok": True, "portfolio": True}

@app.post("/api/refunds/reconcile")
def reconcile(payload: dict):
    return refunds.reconcile(payload.get("transactions", []), payload.get("control_rows", []))

@app.get("/api/monitoring/summary")
def monitoring_summary():
    return monitoring.summary()
