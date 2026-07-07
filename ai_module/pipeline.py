from .ocr_engine import extract_text
from .parser import parse_medications
from .utils import format_medications_output


def process_prescription(image_path: str) -> dict:
    """
    Main entry point — takes image path and returns full structured result
    """
    # Step 1: Extract text using OCR
    ocr_result = extract_text(image_path)

    if not ocr_result["success"]:
        return {
            "success": False,
            "error": ocr_result["error"],
            "raw_text": "",
            "medications": []
        }

    raw_text = ocr_result["text"]

    # Step 2: Parse medications from text
    medications = parse_medications(raw_text)

    # Step 3: Clean/normalize before handing off (e.g. to the DB or frontend)
    formatted_medications = format_medications_output(medications)

    return {
        "success": True,
        "error": None,
        "raw_text": raw_text,
        "medications": formatted_medications
    }
