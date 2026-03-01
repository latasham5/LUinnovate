"""
main.py
FastAPI entry point for The Watchtower backend.
Run: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import (
    audit_router,
    alert_router,
    flag_router,
    training_router,
    scorecard_router,
    supervisor_router,
)

app = FastAPI(
    title="The Watchtower — Developer 3 Backend",
    description="Logging, Alerting, Flag History, Training, Scorecard & Supervisor Access APIs",
    version="1.0.0",
)

# CORS — allow the React + Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite default
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(audit_router)
app.include_router(alert_router)
app.include_router(flag_router)
app.include_router(training_router)
app.include_router(scorecard_router)
app.include_router(supervisor_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "watchtower"}
