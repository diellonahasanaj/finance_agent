from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserOut, UserLogin, UserResponse, PasswordReset, PasswordResetConfirm, EmailVerification, UserProfileUpdate, ChangePassword
from app.services.user_service import register_user, authenticate_user, get_user_by_email, update_user_profile, change_user_password, user_data_to_out, request_password_reset, reset_password, verify_email
from app.utils.jwt import create_access_token
from app.utils.auth import get_current_user
from app.core.config import settings
import logging
from datetime import datetime

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
    """Request a password reset without revealing whether the account exists."""
    try:
        return await request_password_reset(reset_data.email)
    except Exception as e:
        logger.error("Password reset request failed: %s", e)
        raise HTTPException(status_code=500, detail="Unable to process password reset request.")

@router.post("/reset-password", response_model=UserResponse)
async def reset_password_endpoint(reset_data: PasswordResetConfirm):
    """Reset a password using a valid, unexpired reset token."""
    try:
        result = await reset_password(reset_data.token, reset_data.new_password)
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Password reset failed: %s", e)
        raise HTTPException(status_code=500, detail="Unable to reset password.")

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
async def forgot_password(request: PasswordReset):
    """Request a password reset. The development email adapter logs the link."""
    try:
        await request_password_reset(request.email)
        response = {
            "success": True,
            "message": "If an account with this email exists, a password reset link has been sent.",
        }

        if settings.SHOW_DEMO_RESET_LINK and settings.ENV.lower() != "production":
            from app.services.user_service import load_users
            user = load_users().get(request.email.lower())
            if user and user.get("password_reset_token"):
                frontend_url = settings.FRONTEND_URL.rstrip("/")
                response["demo_reset_link"] = f"{frontend_url}/reset-password?token={user['password_reset_token']}"
        return response
    except Exception as e:
        logger.error("Forgot password error: %s", e)
        raise HTTPException(status_code=500, detail="Unable to process password reset request.")

@router.post("/validate-reset-token")
async def validate_reset_token(request: dict):
    """Validate a password reset token without revealing account information."""
    token = request.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")

    from app.services.user_service import load_users
    for user in load_users().values():
        if user.get("password_reset_token") == token:
            expires_at = user.get("password_reset_expires")
            if isinstance(expires_at, datetime):
                if datetime.utcnow() < expires_at:
                    return {"valid": True}
            return {"valid": False}
    return {"valid": False}

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
