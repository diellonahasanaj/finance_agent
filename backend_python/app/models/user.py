from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId

class UserModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str
    email: EmailStr
    hashed_password: str
    created_at: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True
