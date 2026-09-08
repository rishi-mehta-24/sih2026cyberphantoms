import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

key = os.getenv("GEMINI_API_KEY")
print("KEY LENGTH:", len(key) if key else "NONE FOUND")

client = genai.Client(api_key=key)

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Say hello in one short sentence."
)

print(response.text)