from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserOut, UserLogin, UserResponse, PasswordReset, PasswordResetConfirm, EmailVerification, UserProfileUpdate, ChangePassword
from app.services.user_service import register_user, authenticate_user, get_user_by_email, update_user_profile, change_user_password, user_data_to_out, request_password_reset, reset_password, verify_email
from app.utils.jwt import create_access_token
from app.utils.auth import get_current_user
from app.core.config import settings
import logging
import secrets
import re
import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, background_tasks: BackgroundTasks):
    """
    Register a new user with professional validation and security features.
    """
    try:
        logger.info(f"Registration attempt for email: {user.email}")
        logger.info(f"User data: name={user.name}, email={user.email}, password_length={len(user.password)}")
        
        result = await register_user(user)
        
        if result.success:
            logger.info(f"New user registered: {user.email}")
            return result
        else:
            logger.warning(f"Registration failed for {user.email}: {result.message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration. Please try again."
        )

@router.post("/login", response_model=UserResponse)
async def login(user: UserLogin):
    """
    Authenticate user with professional security features including rate limiting.
    """
    try:
        result = await authenticate_user(user.email, user.password, user.remember_me)
        
        if result.success:
            # Create JWT token
            token_data = {"sub": result.user.id}
            
            # Set token expiration based on remember_me
            expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES
            if user.remember_me:
                expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 7  # 7 days for remember me
            
            access_token = create_access_token(token_data, expires_in)
            
            logger.info(f"User logged in: {user.email}")
            
            return UserResponse(
                success=True,
                message=result.message,
                user=result.user,
                access_token=access_token,
                token_type="bearer",
                expires_in=expires_in * 60  # Convert to seconds
            )
        else:
            logger.warning(f"Login failed for {user.email}: {result.message}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.message
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login. Please try again."
        )

@router.post("/login-form", response_model=UserResponse)
async def login_form(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Alternative login endpoint using OAuth2PasswordRequestForm for compatibility.
    """
    user_login = UserLogin(email=form_data.username, password=form_data.password)
    return await login(user_login)

@router.post("/verify-email", response_model=UserResponse)
async def verify_email_endpoint(verification_data: EmailVerification):
    """
    Verify user email using verification token.
    """
    try:
        result = await verify_email(verification_data.token)
        
        if result.success:
            logger.info(f"Email verified successfully for user ID: {result.user.id}")
            return result
        else:
            logger.warning(f"Email verification failed: {result.message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during email verification. Please try again."
        )

@router.post("/request-password-reset", response_model=UserResponse)
async def request_password_reset_endpoint(reset_data: PasswordReset):
    """
    Request password reset for user email.
    """
    try:
        result = await request_password_reset(reset_data.email)
        logger.info(f"Password reset requested for: {reset_data.email}")
        return result
    except Exception as e:
        logger.error(f"Password reset request error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again."
        )

@router.post("/reset-password", response_model=UserResponse)
async def reset_password_endpoint(reset_data: PasswordResetConfirm):
    """
    Reset user password using reset token.
    """
    try:
        result = await reset_password(reset_data.token, reset_data.new_password)
        
        if result.success:
            logger.info("Password reset successfully")
            return result
        else:
            logger.warning(f"Password reset failed: {result.message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during password reset. Please try again."
        )

@router.get("/me", response_model=UserOut)
async def get_current_user_profile(current_user = Depends(get_current_user)):
    """
    Get current user profile.
    """
    return user_data_to_out(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(profile: UserProfileUpdate, current_user=Depends(get_current_user)):
    """Update user profile and financial preferences."""
    result = await update_user_profile(current_user["email"], profile)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


@router.post("/change-password", response_model=UserResponse)
async def change_password(data: ChangePassword, current_user=Depends(get_current_user)):
    """Change the current user's password."""
    result = await change_user_password(current_user["email"], data.current_password, data.new_password)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


@router.post("/forgot-password")
async def forgot_password(request: dict):
    """Send password reset email to user."""
    try:
        email = request.get('email')
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        # Check if user exists
        user = await get_user_by_email(email)
        if not user:
            # Don't reveal if email exists or not for security
            return {"success": True, "message": "If an account with this email exists, a password reset link has been sent."}
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        expiry_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expires in 1 hour
        
        # Store reset token in users file for demo
        from app.services.user_service import load_users, save_users
        users = load_users()
        
        if email.lower() in users:
            users[email.lower()]['password_reset_token'] = reset_token
            users[email.lower()]['password_reset_expires'] = expiry_time.isoformat()
            save_users(users)
        
        # Generate reset link
        reset_link = f"http://localhost:5173/reset-password?token={reset_token}"
        
        # Log the reset link (in production, this would be sent via email)
        print("=" * 60)
        print("PASSWORD RESET EMAIL SIMULATION")
        print("=" * 60)
        print(f"To: {email}")
        print(f"Subject: Reset Your Password")
        print(f"Body: Click the link below to reset your password:")
        print(f"Link: {reset_link}")
        print(f"Token expires in: 1 hour")
        print("=" * 60)
        
        return {
            "success": True, 
            "message": "Password reset instructions have been sent to your email.",
            "debug_info": {
                "email": email,
                "reset_link": reset_link,
                "token": reset_token,
                "expires_at": expiry_time.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Forgot password error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send password reset email. Please try again.")

@router.post("/validate-reset-token")
async def validate_reset_token(request: dict):
    """Validate password reset token."""
    try:
        token = request.get('token')
        if not token:
            raise HTTPException(status_code=400, detail="Token is required")
        
        # Check if token exists in any user record
        from app.services.user_service import load_users
        users = load_users()
        
        token_valid = False
        for email, user_data in users.items():
            if user_data.get('password_reset_token') == token:
                # Check if token is expired
                expires_at = user_data.get('password_reset_expires')
                if expires_at:
                    expiry_time = datetime.datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    if datetime.datetime.utcnow() < expiry_time:
                        token_valid = True
                        break
        
        return {"valid": token_valid}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Token validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-password")
async def reset_password(request: dict):
    """Reset user password using token."""
    try:
        token = request.get('token')
        new_password = request.get('password')
        
        if not token or not new_password:
            raise HTTPException(status_code=400, detail="Token and password are required")
        
        # Validate password
        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', new_password):
            raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', new_password):
            raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', new_password):
            raise HTTPException(status_code=400, detail="Password must contain at least one number")
        
        # Find user with this reset token
        from app.services.user_service import load_users, save_users
        users = load_users()
        
        user_email = None
        for email, user_data in users.items():
            if user_data.get('password_reset_token') == token:
                # Check if token is expired
                expires_at = user_data.get('password_reset_expires')
                if expires_at:
                    expiry_time = datetime.datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    if datetime.datetime.utcnow() < expiry_time:
                        user_email = email
                        break
        
        if not user_email:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        # Hash new password
        from app.utils.password import hash_password
        hashed_password = await hash_password(new_password)
        
        # Update user password and clear reset token
        users[user_email]['hashed_password'] = hashed_password
        users[user_email]['password_reset_token'] = None
        users[user_email]['password_reset_expires'] = None
        users[user_email]['login_attempts'] = 0  # Reset login attempts
        users[user_email]['locked_until'] = None  # Unlock account if locked
        
        save_users(users)
        
        print(f"Password reset successful for {user_email}")
        
        return {
            "success": True,
            "message": "Password has been reset successfully. You can now sign in with your new password."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Password reset error: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset password. Please try again.")

@router.post("/verify-user-manually")
async def verify_user_manually(request: dict):
    """Manually verify a user (for testing purposes)."""
    try:
        email = request.get('email')
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        # Load users and update verification status
        from app.services.user_service import load_users, save_users
        users = load_users()
        
        if email.lower() in users:
            users[email.lower()]['is_verified'] = True
            save_users(users)
            return {"success": True, "message": f"User {email} has been verified."}
        else:
            raise HTTPException(status_code=404, detail="User not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout")
async def logout():
    """
    Logout endpoint. In a stateless JWT system, actual logout happens on the client side
    by removing the token. This endpoint can be used for logging or to invalidate tokens
    if using a token blacklist system.
    """
    logger.info("User logged out")
    return {"message": "Successfully logged out"}
