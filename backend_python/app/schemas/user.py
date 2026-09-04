from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re
from datetime import datetime

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name must be between 2 and 100 characters")
    email: EmailStr = Field(..., description="Valid email address required")
    password: str = Field(..., min_length=8, max_length=128, description="Password must be at least 8 characters long")
    
    @validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z\s\-\.]+$', v):
            raise ValueError('Name can only contain letters, spaces, hyphens, and periods')
        return v.strip().title()
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Valid email address required")
    password: str = Field(..., min_length=1, description="Password is required")
    remember_me: bool = Field(default=False, description="Keep user logged in")

class UserOut(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    last_login: Optional[datetime] = None
    monthly_income: Optional[float] = None
    savings_goal: Optional[float] = None
    currency: str = "USD"
    
    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserOut] = None
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    expires_in: Optional[int] = None

class PasswordReset(BaseModel):
    email: EmailStr = Field(..., description="Email address for password reset")

class PasswordResetConfirm(BaseModel):
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password must be at least 8 characters long")
    
    @validator('new_password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class EmailVerification(BaseModel):
    token: str = Field(..., description="Email verification token")

class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    monthly_income: Optional[float] = Field(default=None, ge=0)
    savings_goal: Optional[float] = Field(default=None, ge=0)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)

class ChangePassword(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)

    @validator('new_password')
    def validate_new_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
