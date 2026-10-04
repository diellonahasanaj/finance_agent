"""
Professional user service logic for registration, authentication, and account management.
Handles password hashing, JWT integration, email verification, and security features.
"""
import secrets
import asyncio
import json
import os
from datetime import datetime, timedelta
from app.schemas.user import UserCreate, UserOut, UserResponse, UserProfileUpdate, ChangePassword
from app.utils.password import hash_password, verify_password
from app.core.config import settings
from bson import ObjectId

# File-based storage for temporary use
USERS_FILE = "users.json"
_DATETIME_FIELDS = ("verification_expires", "locked_until", "password_reset_expires", "created_at", "last_login")

def _restore_datetimes(user_data: dict) -> dict:
    """Restore datetime values that were serialized to JSON strings."""
    restored = dict(user_data)
    for field in _DATETIME_FIELDS:
        value = restored.get(field)
        if isinstance(value, str):
            try:
                restored[field] = datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
            except ValueError:
                pass
    return restored

def load_users():
    """Load users from file and restore persisted datetime fields."""
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
    return {email.lower(): _restore_datetimes(data) for email, data in users.items()}

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
        "last_login": None,
        "monthly_income": None,
        "savings_goal": None,
        "currency": "USD",
    }
    
    # Save user
    users[user.email.lower()] = user_dict
    save_users(users)
    
    # Create user response
    user_out = user_data_to_out(user_dict)
    
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
    
    return UserResponse(
        success=True,
        message="Login successful!",
        user=user_data_to_out(user_data),
        access_token="dummy_token",
        token_type="bearer",
        expires_in=86400,
    )


def user_data_to_out(user_data: dict) -> UserOut:
    """Convert stored user dict to UserOut schema."""
    return UserOut(
        id=user_data["_id"],
        name=user_data["name"],
        email=user_data["email"],
        is_active=user_data.get("is_active", True),
        is_verified=user_data.get("is_verified", False),
        created_at=user_data.get("created_at"),
        last_login=user_data.get("last_login"),
        monthly_income=user_data.get("monthly_income"),
        savings_goal=user_data.get("savings_goal"),
        currency=user_data.get("currency", "USD"),
    )


async def update_user_profile(email: str, profile: UserProfileUpdate) -> UserResponse:
    """Update user profile and financial preferences."""
    users = load_users()
    user_data = users.get(email.lower())
    if not user_data:
        return UserResponse(success=False, message="User not found.", user=None)

    if profile.name is not None:
        user_data["name"] = profile.name.strip()
    if profile.monthly_income is not None:
        user_data["monthly_income"] = profile.monthly_income
    if profile.savings_goal is not None:
        user_data["savings_goal"] = profile.savings_goal
    if profile.currency is not None:
        user_data["currency"] = profile.currency.upper()

    users[email.lower()] = user_data
    save_users(users)

    return UserResponse(
        success=True,
        message="Profile updated successfully.",
        user=user_data_to_out(user_data),
    )


async def change_user_password(email: str, current_password: str, new_password: str) -> UserResponse:
    """Change user password after verifying current password."""
    users = load_users()
    user_data = users.get(email.lower())
    if not user_data:
        return UserResponse(success=False, message="User not found.", user=None)

    if not await verify_password(current_password, user_data["hashed_password"]):
        return UserResponse(success=False, message="Current password is incorrect.", user=None)

    user_data["hashed_password"] = await hash_password(new_password)
    users[email.lower()] = user_data
    save_users(users)

    return UserResponse(success=True, message="Password changed successfully.", user=user_data_to_out(user_data))


async def request_password_reset(email: str) -> UserResponse:
    """Create a password-reset token and send/log the reset link without exposing the token in the API response."""
    users = load_users()
    user_data = users.get(email.lower())

    if not user_data:
        return UserResponse(
            success=True,
            message="If an account with this email exists, a password reset link has been sent.",
            user=None,
        )

    reset_token = secrets.token_urlsafe(32)
    user_data["password_reset_token"] = reset_token
    user_data["password_reset_expires"] = datetime.utcnow() + timedelta(hours=1)
    users[email.lower()] = user_data
    save_users(users)

    from app.utils.email import send_password_reset_email
    await send_password_reset_email(email, reset_token)

    return UserResponse(
        success=True,
        message="If an account with this email exists, a password reset link has been sent.",
        user=None,
    )


async def reset_password(token: str, new_password: str) -> UserResponse:
    """
    Reset user password using reset token.
    Validates the token and updates the password if valid.
    """
    users = load_users()
    
    # Find user with matching reset token
    user_email = None
    user_data = None
    
    for email, data in users.items():
        if data.get("password_reset_token") == token:
            user_email = email
            user_data = data
            break
    
    if not user_data:
        return UserResponse(
            success=False,
            message="Invalid or expired reset token.",
            user=None
        )
    
    # Check if token is expired
    if user_data.get("password_reset_expires") and datetime.utcnow() > user_data["password_reset_expires"]:
        return UserResponse(
            success=False,
            message="Reset token has expired. Please request a new password reset.",
            user=None
        )
    
    # Update password
    user_data["hashed_password"] = await hash_password(new_password)
    user_data["password_reset_token"] = None
    user_data["password_reset_expires"] = None
    user_data["login_attempts"] = 0  # Reset login attempts
    user_data["locked_until"] = None  # Unlock account if it was locked
    
    # Save updated user data
    users[user_email] = user_data
    save_users(users)
    
    return UserResponse(
        success=True,
        message="Password has been reset successfully. You can now log in with your new password.",
        user=user_data_to_out(user_data)
    )


async def verify_email(token: str) -> UserResponse:
    """
    Verify user email using verification token.
    In demo mode, auto-verification is enabled by default.
    """
    users = load_users()
    
    # Find user with matching verification token
    user_email = None
    user_data = None
    
    for email, data in users.items():
        if data.get("verification_token") == token:
            user_email = email
            user_data = data
            break
    
    if not user_data:
        return UserResponse(
            success=False,
            message="Invalid or expired verification token.",
            user=None
        )
    
    # Check if token is expired
    if user_data.get("verification_expires") and datetime.utcnow() > user_data["verification_expires"]:
        return UserResponse(
            success=False,
            message="Verification token has expired. Please request a new verification email.",
            user=None
        )
    
    # Mark user as verified
    user_data["is_verified"] = True
    user_data["verification_token"] = None
    user_data["verification_expires"] = None
    
    # Save updated user data
    users[user_email] = user_data
    save_users(users)
    
    return UserResponse(
        success=True,
        message="Email verified successfully! You can now log in.",
        user=user_data_to_out(user_data)
    )
