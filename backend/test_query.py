import sys
sys.path.append("/home/amg/Desktop/CodeVeil/backend")
from app.core.auth.jwt import create_access_token
import requests
from pymongo import MongoClient

token = create_access_token({'user_id': '667be9d9a10123456789abcd'})

client = MongoClient("mongodb+srv://amoghavaiyer_db_user:QTuWfN2oYG37p7iS@cluster0.3a7dkye.mongodb.net/?appName=Cluster0")
repo = client.codeveil.repositories.find_one()
if not repo:
    print("No repo found")
    sys.exit(1)
    
repo_id = str(repo["_id"])
print(f"Using repo: {repo_id}")

res = requests.post(
    "http://localhost:8000/query",
    json={"repo_id": repo_id, "question": "give me the flow of the retrieval pipeline"},
    headers={"Authorization": f"Bearer {token}"}
)

print("Status code:", res.status_code)
print("Response text:", res.text)
