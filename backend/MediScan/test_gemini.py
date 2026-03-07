import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
print(f"API Key loaded: {api_key[:10]}...")

# NEW API
client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents="Say hello!"
)

print(response.text)