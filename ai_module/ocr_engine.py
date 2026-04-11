import os
import base64
from groq import Groq


def encode_image(image_path: str) -> str:
    """Convert image to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def extract_text(image_path: str) -> dict:
    """
    Uses Groq Vision to extract medication info directly from image
    """
    if not os.path.exists(image_path):
        return {"success": False, "text": "", "error": "Image not found"}

    try:
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))

        # Encode image to base64
        base64_image = encode_image(image_path)

        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
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
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=200
        )

        text = response.choices[0].message.content.strip()

        if not text:
            return {"success": False, "text": "", "error": "No text detected"}

        return {"success": True, "text": text, "error": None}

    except Exception as e:
        return {"success": False, "text": "", "error": str(e)}