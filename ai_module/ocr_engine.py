import easyocr
import os

# Initialize reader once (English only)
reader = easyocr.Reader(['en'], gpu=False)


def extract_text(image_path: str) -> dict:
    """
    Takes image path and returns raw extracted text using EasyOCR
    """
    if not os.path.exists(image_path):
        return {"success": False, "text": "", "error": "Image not found"}

    try:
        results = reader.readtext(image_path)

        if not results:
            return {"success": False, "text": "", "error": "No text detected"}

        # Join all detected text pieces
        text = " ".join([result[1] for result in results])

        return {"success": True, "text": text, "error": None}

    except Exception as e:
        return {"success": False, "text": "", "error": str(e)}