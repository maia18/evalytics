"""Configuração e clientes dos serviços usados pela API."""

import logging
import os
from pathlib import Path

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import firestore, storage

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("evalytics.api")

PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
BUCKET_NAME = os.getenv("FIREBASE_STORAGE_BUCKET")

if not PROJECT_ID or not BUCKET_NAME:
    raise RuntimeError(
        "Defina FIREBASE_PROJECT_ID e FIREBASE_STORAGE_BUCKET no .env."
    )

MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "10")) * 1024 * 1024
MAX_FILES_PER_EVALUATION = int(os.getenv("MAX_FILES_PER_EVALUATION", "100"))
MAX_FILES_PER_INDICATOR = int(os.getenv("MAX_FILES_PER_INDICATOR", "20"))
INSTITUICAO_PADRAO_ID = os.getenv("EVALYTICS_INSTITUICAO_ID", "ufc").strip() or "ufc"

if min(MAX_FILE_SIZE, MAX_FILES_PER_EVALUATION, MAX_FILES_PER_INDICATOR) <= 0:
    raise RuntimeError("Os limites de arquivos devem ser maiores que zero.")

if not firebase_admin._apps:
    firebase_admin.initialize_app(
        options={
            "projectId": PROJECT_ID,
            "storageBucket": BUCKET_NAME,
        }
    )

db = firestore.client()
bucket = storage.bucket()
