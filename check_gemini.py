
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise SystemExit("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        contents="Reply with exactly: Gemini is working"
    )
    print("SUCCESS:", response.text)
except Exception as error:
    print("GEMINI ERROR:", error)
finally:
    client.close()
