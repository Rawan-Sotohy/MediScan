from google import genai
import os

api_key = os.getenv('GOOGLE_API_KEY')
client = genai.Client(api_key=api_key)

prompt = "Hello, can you say hi in 3 words?"
response = client.models.generate_content(
    model='gemini-1.5-flash',
    contents=prompt
)

print(response.text)
