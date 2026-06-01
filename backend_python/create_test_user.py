import asyncio
import sys
sys.path.append('.')
from app.services.user_service import register_user
from app.schemas.user import UserCreate

async def create_test_user():
    # Create a test user with known password
    test_user = UserCreate(
        name="Test User",
        email="test@example.com",
        password="test123"
    )
    
    result = await register_user(test_user)
    print('Registration result:', result.success)
    print('Message:', result.message)
    if result.user:
        print('User created:', result.user.name, result.user.email)

if __name__ == '__main__':
    asyncio.run(create_test_user())
