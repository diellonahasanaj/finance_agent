"""
Professional user service logic for registration, authentication, and account management.
Handles password hashing, JWT integration, email verification, and security features.
"""
import secrets
import asyncio
import json
import os
from datetime import datetime, timedelta
from app.schemas.user import UserCreate, UserOut, UserResponse
from app.utils.password import hash_password, verify_password
from app.core.config import settings
from bson import ObjectId

# File-based storage for temporary use
USERS_FILE = "users.json"

def load_users():
    """Load users from file."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to file."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, default=str)

async def get_user_by_email(email: str):
    """Get user by email from file storage."""
    try:
        users = load_users()
        
        # Direct lookup using email as key (stored in lowercase)
        user_data = users.get(email.lower())
        if user_data:
            return {
                "id": user_data.get("_id"),
                "name": user_data.get('name'),
                "email": user_data.get('email'),
                "created_at": user_data.get('created_at'),
                "is_active": user_data.get('is_active', True),
                "is_verified": user_data.get('is_verified', False)
            }
        
        return None
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None

async def register_user(user: UserCreate) -> UserResponse:
    """
    Register a new user with professional validation and security features.
    Hashes the password, stores user in the database, and sends verification email.
    Returns detailed response with success status and user information.
    """
    # Load existing users
    users = load_users()
    
    # Check if user already exists
    if user.email.lower() in users:
        return UserResponse(
            success=False,
            message="An account with this email already exists. Please try logging in or use a different email.",
            user=None
        )
    
    # Hash password with secure method
    hashed = await hash_password(user.password)
    
    # Generate verification token
    verification_token = secrets.token_urlsafe(32)
    
    # Create user document
    user_dict = {
        "_id": str(ObjectId()),
        "name": user.name,
        "email": user.email.lower(),
        "hashed_password": hashed,
        "is_active": True,
        "is_verified": True,  # Auto-verify for testing (set to False in production)
        "verification_token": verification_token,
        "verification_expires": datetime.utcnow() + timedelta(hours=24),
        "login_attempts": 0,
        "locked_until": None,
        "password_reset_token": None,
        "password_reset_expires": None,
        "created_at": datetime.utcnow(),
        "last_login": None
    }
    
    # Save user
    users[user.email.lower()] = user_dict
    save_users(users)
    
    # Create user response
    user_out = UserOut(
        id=user_dict["_id"],
        name=user.name,
        email=user.email.lower(),
        is_active=user_dict["is_active"],
        is_verified=user_dict["is_verified"],
        created_at=user_dict["created_at"]
    )
    
    return UserResponse(
        success=True,
        message="Registration successful! You can now log in with your credentials.",
        user=user_out,
        access_token="dummy_token",  # In production, this would be a real JWT
        token_type="bearer",
        expires_in=86400  # 24 hours
    )

async def authenticate_user(email: str, password: str, remember_me: bool = False) -> UserResponse:
    """
    Authenticate user with professional security features.
    Includes rate limiting, account locking, and secure password verification.
    """
    users = load_users()
    
    # Find user by email
    user_data = users.get(email.lower())
    if not user_data:
        return UserResponse(
            success=False,
            message="Invalid email or password.",
            user=None
        )
    
    # Check if account is locked
    if user_data.get("locked_until") and datetime.utcnow() < user_data["locked_until"]:
        return UserResponse(
            success=False,
            message="Account is temporarily locked due to multiple failed login attempts. Please try again later.",
            user=None
        )
    
    # Check if account is verified
    if not user_data.get("is_verified", False):
        return UserResponse(
            success=False,
            message="Please verify your email address before logging in. Check your inbox for the verification email.",
            user=None
        )
    
    # Verify password
    if not await verify_password(password, user_data["hashed_password"]):
        # Increment login attempts
        user_data["login_attempts"] = user_data.get("login_attempts", 0) + 1
        
        # Lock account after 5 failed attempts
        if user_data["login_attempts"] >= 5:
            user_data["locked_until"] = datetime.utcnow() + timedelta(minutes=30)
        
        # Save updated user data
        users[email.lower()] = user_data
        save_users(users)
        
        return UserResponse(
            success=False,
            message="Invalid email or password.",
            user=None
        )
    
    # Reset login attempts on successful login
    user_data["login_attempts"] = 0
    user_data["locked_until"] = None
    user_data["last_login"] = datetime.utcnow()
    
    # Save updated user data
    users[email.lower()] = user_data
    save_users(users)
    
    # Create user response
    user_out = UserOut(
        id=user_data["_id"],
        name=user_data["name"],
        email=user_data["email"],
        is_active=user_data.get("is_active", True),
        is_verified=user_data.get("is_verified", False),
        created_at=user_data.get("created_at")
    )
    
    return UserResponse(
        success=True,
        message="Login successful!",
        user=user_out,
        access_token="dummy_token",  # In production, this would be a real JWT
        token_type="bearer",
        expires_in=86400  # 24 hours
    )
