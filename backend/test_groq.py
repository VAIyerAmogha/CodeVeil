import sys
import os

# add backend dir to sys path
sys.path.append("/home/amg/Desktop/CodeVeil/backend")
from app.config import settings
print("Settings api key:", settings.groq_api_key)
print("Settings api keys:", settings.groq_api_keys)

from app.generation.responder import _get_groq_api_key, groq_client
print("API Key:", _get_groq_api_key())
print("Groq Client:", groq_client)

if groq_client:
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": "hello"}],
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )
        print("Response:", response.choices[0].message.content)
    except Exception as e:
        print("Error during generation:", e)
