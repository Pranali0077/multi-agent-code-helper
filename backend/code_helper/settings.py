"""Settings and configuration loader for code_helper.
Loads backend/code_helper/.env lazily and exposes settings with clean error handling.
"""
from pathlib import Path
import os
from dotenv import load_dotenv

# Path to the .env file in backend/code_helper/.env
ENV_PATH = Path(__file__).resolve().parent / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

def get_env(name: str, default: str | None = None) -> str:
    val = os.getenv(name, default)
    if val is None or val == "":
        raise ValueError(
            f"Missing required environment variable: '{name}'. "
            "Please configure it in backend/code_helper/.env"
        )
    return val

# General models and constants
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
NVIDIA_EMBED_MODEL = os.getenv("NVIDIA_EMBED_MODEL", "nvidia_nim/nvidia/nemotron-3-embed-1b")
EMBED_DIM = int(os.getenv("EMBED_DIM", "2048"))

PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "code-helper")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")

def get_google_api_key() -> str:
    return get_env("GOOGLE_API_KEY")

def get_nvidia_api_key() -> str:
    key = os.getenv("NVIDIA_API_KEY") or os.getenv("NVIDIA_NIM_API_KEY")
    if not key:
        raise ValueError(
            "Missing required environment variable: 'NVIDIA_API_KEY' or 'NVIDIA_NIM_API_KEY'. "
            "Please configure it in backend/code_helper/.env"
        )
    return key

def get_pinecone_api_key() -> str:
    return get_env("PINECONE_API_KEY")

def get_target_project_path() -> Path:
    raw = get_env("TARGET_PROJECT_PATH")
    p = Path(raw).resolve()
    if not p.exists():
        raise FileNotFoundError(f"TARGET_PROJECT_PATH does not exist: {p}")
    return p
