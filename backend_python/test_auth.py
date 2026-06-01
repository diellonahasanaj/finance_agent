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
    if email.lower() in users:
        user_data = users[email.lower()]
        print('User found:', user_data['name'])
        print('Stored hash:', user_data['hashed_password'])
        
        # Test different passwords
        test_passwords = ['test123', 'Test123', 'password', 'Password']
        stored_hash = user_data['hashed_password']
        
        for pwd in test_passwords:
            try:
                result = bcrypt.checkpw(pwd.encode('utf-8'), stored_hash.encode('utf-8'))
                print(f'Password "{pwd}": {result}')
            except Exception as e:
                print(f'Error checking "{pwd}": {e}')
    
    # Test actual authentication
    result = await authenticate_user(email, 'test123')
    print('\nAuthentication result:', result.success)
    print('Message:', result.message)

if __name__ == '__main__':
    asyncio.run(test_login())
