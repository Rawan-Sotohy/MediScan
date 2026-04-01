import os
from pathlib import Path


ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}
MAX_FILE_SIZE_MB = 10


def is_valid_image(file_path: str) -> dict:
    """
    Checks if file exists, has valid extension, and is within size limit
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