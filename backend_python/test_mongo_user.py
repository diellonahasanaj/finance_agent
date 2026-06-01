#!/usr/bin/env python3
"""
Test MongoDB user lookup
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def test_user():
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client.get_default_database()
    users_collection = db["users"]
    
    user_id = "699d72ca2caaa7f5b8565ef1"
    print(f"Looking for user with _id: {user_id}")
    
    user = await users_collection.find_one({"_id": user_id})
    print(f"Found user: {user}")
    
    if user:
        print(f"User _id: {user.get('_id')}")
        print(f"User email: {user.get('email')}")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(test_user())
