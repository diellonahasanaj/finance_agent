#!/usr/bin/env python3
"""
Test login endpoint directly
"""
import asyncio
import sys
import bcrypt
sys.path.append('.')
from app.services.user_service import authenticate_user, load_users

async def test_login():
    # Load users to see what's stored
    users = load_users()
    print('Stored users:', users.keys())
    
    # Test with stored hash
    email = 'diellona.hasanaj@umib.net'
    password = 'password123'
    
    if email.lower() in users:
        user_data = users[email.lower()]
        print('User found:', user_data['name'])
        print('Is verified:', user_data.get('is_verified', False))
        print('Login attempts:', user_data.get('login_attempts', 0))
        print('Locked until:', user_data.get('locked_until'))
        
        # Test password verification
        stored_hash = user_data['hashed_password']
        result = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        print(f'Password verification: {result}')
    
    # Test actual authentication
    result = await authenticate_user(email, password)
    print('\nAuthentication result:', result.success)
    print('Message:', result.message)
    if result.user:
        print('Authenticated user:', result.user.name)

if __name__ == '__main__':
    asyncio.run(test_login())
