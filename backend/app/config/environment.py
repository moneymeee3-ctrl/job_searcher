"""EMBEDHUNT AI — Environment helpers"""
import os
def get_env(key: str, default: str = "") -> str: return os.getenv(key, default)
def require_env(key: str) -> str:
    v = os.getenv(key)
    if not v: raise RuntimeError(f"Required environment variable missing: {key}")
    return v
