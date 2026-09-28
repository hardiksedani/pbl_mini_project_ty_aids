import os
from functools import lru_cache

import firebase_admin
from firebase_admin import credentials, firestore, storage
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    firebase_project_id: str = ""
    firebase_storage_bucket: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


def init_firebase() -> None:
    """Initialize Firebase Admin SDK (local key or ADC)."""
    if firebase_admin._apps:
        return

    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    settings = get_settings()

    if cred_path and os.path.isfile(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(
            cred,
            {"storageBucket": settings.firebase_storage_bucket},
        )
    else:
        firebase_admin.initialize_app(
            options={"storageBucket": settings.firebase_storage_bucket},
        )


def get_firestore_client():
    init_firebase()
    return firestore.client()


def get_storage_bucket():
    init_firebase()
    return storage.bucket()
