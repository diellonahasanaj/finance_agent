#!/usr/bin/env python3
"""
Test MongoDB connection
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def test_mongo():
    try:
        print("Testing MongoDB connection...")
        client = AsyncIOMotorClient(settings.MONGO_URI)
        db = client.get_default_database()
        
        # Test connection by getting server info
        server_info = await client.server_info()
        print(f"✅ MongoDB connected successfully")
        print(f"   Server version: {server_info.get('version')}")
        
        # Test collections
        collections = await db.list_collection_names()
        print(f"   Collections: {collections}")
        
        # Test users collection
        users_collection = db["users"]
        count = await users_collection.count_documents({})
        print(f"   Users count: {count}")
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print(f"   Connection string: {settings.MONGO_URI}")

if __name__ == "__main__":
    asyncio.run(test_mongo())
