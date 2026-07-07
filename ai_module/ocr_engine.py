import os
import base64
import mimetypes
from groq import Groq

from .utils import is_valid_image, with_retry


# Configurable via .env, so if Groq deprecates this model again in the future
# (like it did with llama-4-scout), we only need to change GROQ_VISION_MODEL -
# no code changes required.
VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "qwen/qwen3.6-27b")


def encode_image(image_path: str) -> tuple:
    """
    Convert image to base64 and detect its real MIME type (instead of
    always assuming jpeg, which breaks results for png uploads).
    """
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type or not mime_type.startswith("image/"):
        mime_type = "image/jpeg"

    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode('utf-8')

    return encoded, mime_type


@with_retry(max_retries=3, base_delay=2)
def _call_vision_model(client: Groq, base64_image: str, mime_type: str):
    return client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """This is a handwritten medical prescription.
Extract ALL medication names you can see.
Return ONLY the medication names, one per line.
Nothing else - no explanations, no dosage, just the names."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=200
    )


def extract_text(image_path: str) -> dict:
    """
    Uses Groq Vision to extract medication info directly from image
    """
    validation = is_valid_image(image_path)
    if not validation["valid"]:
        return {"success": False, "text": "", "error": validation["error"]}

    try:
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        base64_image, mime_type = encode_image(image_path)

        response = _call_vision_model(client, base64_image, mime_type)
        text = response.choices[0].message.content.strip()

        if not text:
            return {"success": False, "text": "", "error": "No text detected"}

        return {"success": True, "text": text, "error": None}

    except Exception as e:
        return {"success": False, "text": "", "error": str(e)}
