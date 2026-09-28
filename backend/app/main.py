import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    analytics,
    dashboard,
    data,
    data_list,
    export,
    pipeline,
    predict,
    scenario,
    search,
    states,
    train,
)
from app.services.firebase import init_firebase

load_dotenv()

app = FastAPI(
    title="AI-Powered El Niño Agricultural Economic Intelligence Platform API",
    description="Panel-data Machine Learning & Scenario Intelligence Platform for Indian Agricultural Output.",
    version="2.0.0",
)

origins = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router)
app.include_router(data_list.router)
app.include_router(pipeline.router)
app.include_router(train.router)
app.include_router(predict.router)
app.include_router(scenario.router)
app.include_router(search.router)
app.include_router(analytics.router)
app.include_router(export.router)
app.include_router(states.router)
app.include_router(dashboard.router)


@app.on_event("startup")
async def startup():
    try:
        init_firebase()
    except Exception as exc:
        import logging
        logging.getLogger(__name__).info("Firebase initialization deferred or using local storage: %s", exc)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "platform": "El Niño Agricultural Economic Intelligence Platform",
        "institution": "K. J. Somaiya Institute of Technology",
    }
