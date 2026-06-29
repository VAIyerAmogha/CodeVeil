import asyncio
import httpx
from app.config import settings
async def test():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={settings.gemini_api_key}"
    payload = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": "hello"}]},
        "outputDimensionality": 768
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
        print("Status:", r.status_code)
        if r.status_code == 200:
            print("Dims:", len(r.json()["embedding"]["values"]))
        else:
            print(r.text)
asyncio.run(test())
