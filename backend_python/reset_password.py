import bcrypt
import json

def reset_user_password():
    """Reset user password to a known value for testing"""
    
    # Load current users
    with open('users.json', 'r') as f:
        users = json.load(f)
    
    email = 'diellona.hasanaj@umib.net'
    new_password = 'password123'  # 8+ characters as required
    
    # Generate new hash
    new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Update user password
    if email.lower() in users:
        users[email.lower()]['hashed_password'] = new_hash
        users[email.lower()]['is_verified'] = True  # Ensure verified
        users[email.lower()]['login_attempts'] = 0  # Reset login attempts
        
        # Save updated users
        with open('users.json', 'w') as f:
            json.dump(users, f, default=str)
        
        print(f"Password reset for {email}")
        print(f"New password: {new_password}")
        print(f"New hash: {new_hash}")
        
        # Test the new password
        test_result = bcrypt.checkpw(new_password.encode('utf-8'), new_hash.encode('utf-8'))
        print(f"Password verification test: {test_result}")
        
    else:
        print(f"User {email} not found")

if __name__ == '__main__':
    reset_user_password()
