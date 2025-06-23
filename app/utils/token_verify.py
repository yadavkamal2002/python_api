from fastapi import HTTPException, Depends
from fastapi.security import APIKeyHeader
from decouple import config

API_TOKEN = config("API_TOKEN")  # Fetch token from .env

api_key_header = APIKeyHeader(name='x-access-tokens')  # Header name to extract token

def token_required(api_key: str = Depends(api_key_header)):
    print(f"Received API Key: {api_key}")  # Debugging the token received
    if not api_key or api_key != API_TOKEN:
        raise HTTPException(status_code=403, detail="Token is missing or invalid!")
    return api_key
