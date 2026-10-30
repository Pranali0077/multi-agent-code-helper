"""Settings and configuration loader for code_helper.
Loads backend/code_helper/.env lazily and exposes settings with clean error handling.
"""
from pathlib import Path
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger("code_helper.settings")

# Path to the .env file in backend/code_helper/.env and backend/.env
CODE_HELPER_ENV = Path(__file__).resolve().parent / ".env"
BACKEND_ENV = Path(__file__).resolve().parent.parent / ".env"

if CODE_HELPER_ENV.exists():
    ENV_PATH = CODE_HELPER_ENV
    load_dotenv(dotenv_path=CODE_HELPER_ENV, override=True)
elif BACKEND_ENV.exists():
    ENV_PATH = BACKEND_ENV
    load_dotenv(dotenv_path=BACKEND_ENV, override=True)
else:
    ENV_PATH = CODE_HELPER_ENV
    load_dotenv(override=True)

def get_env(name: str, default: str | None = None) -> str:
    val = os.getenv(name, default)
    if val is None or val == "":
        raise ValueError(
            f"Missing required environment variable: '{name}'. "
            "Please configure it in backend/code_helper/.env"
        )
    return val.strip().strip("\"'")

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
    return key.strip().strip("\"'")

def get_pinecone_api_key() -> str:
    key = get_env("PINECONE_API_KEY")
    # Defensively detect if multiple pcsk_ keys were accidentally concatenated
    if key.count("pcsk_") > 1:
        last_pos = key.rfind("pcsk_")
        logger.warning(
            "Detected multiple concatenated Pinecone API keys in PINECONE_API_KEY. "
            "Using the latest key starting at index %d.", last_pos
        )
        key = key[last_pos:]
    return key

def get_target_project_path() -> Path:
    raw = get_env("TARGET_PROJECT_PATH")
    p = Path(raw).resolve()
    if not p.exists():
        raise FileNotFoundError(f"TARGET_PROJECT_PATH does not exist: {p}")
    return p

def mask_secret(secret: str | None, prefix_len: int = 5, suffix_len: int = 4) -> str:
    """Mask a secret key safely, showing only prefix and suffix without exposing the secret."""
    if not secret:
        return "<NOT SET>"
    s = secret.strip().strip("\"'")
    if len(s) <= prefix_len + suffix_len:
        return f"<SET: len={len(s)}: ***>"
    return f"{s[:prefix_len]}...{s[-suffix_len:]} (len={len(s)})"

def log_env_diagnostics(log_fn=None) -> dict[str, str]:
    """
    Safely inspect and log environment configuration status
    without exposing actual secret values.
    """
    printer = log_fn or logger.info
    diag = {}

    diag["ENV_PATH"] = str(ENV_PATH)
    diag["ENV_EXISTS"] = str(ENV_PATH.exists())

    for key_name in ["GOOGLE_API_KEY", "NVIDIA_API_KEY", "NVIDIA_NIM_API_KEY", "PINECONE_API_KEY"]:
        val = os.getenv(key_name)
        diag[key_name] = mask_secret(val)

    diag["PINECONE_INDEX_NAME"] = PINECONE_INDEX_NAME
    diag["PINECONE_CLOUD"] = PINECONE_CLOUD
    diag["PINECONE_REGION"] = PINECONE_REGION
    diag["EMBED_DIM"] = str(EMBED_DIM)

    raw_target = os.getenv("TARGET_PROJECT_PATH")
    if raw_target:
        p = Path(raw_target).resolve()
        diag["TARGET_PROJECT_PATH"] = f"{p} (exists={p.exists()})"
    else:
        diag["TARGET_PROJECT_PATH"] = "<NOT SET>"

    printer("=== Environment Diagnostics (Safe / Masked) ===")
    for k, v in diag.items():
        printer(f"  {k}: {v}")
    printer("================================================")
    return diag
