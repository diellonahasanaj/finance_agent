from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.utils.jwt import decode_access_token
import json
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

USERS_FILE = "users.json"

def load_users():
    """Load users from file."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # For now, just return a dummy user since we're using dummy tokens
    # In production, this would decode the JWT and find the user
    users = load_users()
    if users:
        # Return the first user for simplicity
        user_data = list(users.values())[0]
        return user_data
    else:
        # If no users exist, create a dummy one
        return {
            "_id": "dummy_user",
            "name": "Dummy User",
            "email": "dummy@example.com",
            "is_active": True,
            "is_verified": True
        }
