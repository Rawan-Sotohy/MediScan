import os
import time
import functools
from pathlib import Path

import groq


ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
MAX_FILE_SIZE_MB = 10


def is_valid_image(file_path: str) -> dict:
    """
    Checks if file exists, has a valid (real image) extension, and is within size limit.
    Note: PDFs are intentionally not allowed here - the OCR pipeline sends the file
    directly to a vision model as an image, so a PDF would silently produce garbage
    results instead of a clear error.
    """
    path = Path(file_path)

    if not path.exists():
        return {"valid": False, "error": "File not found"}

    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return {"valid": False, "error": f"Invalid file type. Allowed: {ALLOWED_EXTENSIONS}"}

    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return {"valid": False, "error": f"File too large. Max size: {MAX_FILE_SIZE_MB}MB"}

    return {"valid": True, "error": None}


def format_medications_output(medications: list) -> list:
    """
    Cleans and formats the medications list before returning to frontend
    """
    formatted = []
    for med in medications:
        formatted.append({
            "name":      med.get("name", "Unknown").strip().title(),
            "dosage":    med.get("dosage", "See prescription"),
            "frequency": med.get("frequency", "As directed"),
            "duration":  med.get("duration", "As directed"),
        })
    return formatted


def with_retry(max_retries: int = 3, base_delay: float = 2.0):
    """
    Decorator for Groq API calls. Automatically retries with exponential
    backoff on rate limits (429) and transient connection/server errors,
    so a single busy moment on Groq's side doesn't fail the user's request.
    Client errors (bad request, auth, invalid model, etc.) are NOT retried -
    retrying those would just waste time and return the same error again.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except groq.RateLimitError as e:
                    last_error = e
                except groq.APIConnectionError as e:
                    last_error = e
                except groq.APIStatusError as e:
                    # Only retry server-side errors (5xx). Anything else
                    # (bad request, invalid API key, model not found...)
                    # will fail again immediately, so raise right away.
                    if 500 <= e.status_code < 600:
                        last_error = e
                    else:
                        raise

                if attempt < max_retries:
                    time.sleep(base_delay * (2 ** attempt))

            raise last_error
        return wrapper
    return decorator
