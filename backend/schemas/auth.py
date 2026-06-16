from pydantic import BaseModel, field_validator
from typing import Optional

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

    @field_validator('username')
    @classmethod
    def username_valid(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric')
        return v.lower()

    @field_validator('password')
    @classmethod
    def password_valid(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    onboarded: bool = False

class TokenData(BaseModel):
    username: Optional[str] = None
