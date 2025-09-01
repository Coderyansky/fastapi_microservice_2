from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional
import re


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 2:
            raise ValueError('Name must be at least 2 characters long')
        if len(v) > 100:
            raise ValueError('Name must not exceed 100 characters')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Za-z]', v) or not re.search(r'[0-9]', v):
            raise ValueError('Password must contain both letters and numbers')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            phone_pattern = r'^(\+7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
            if not re.match(phone_pattern, v):
                raise ValueError('Invalid phone number format')
        return v


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    phone: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if len(v) < 2:
                raise ValueError('Name must be at least 2 characters long')
            if len(v) > 100:
                raise ValueError('Name must not exceed 100 characters')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            phone_pattern = r'^(\+7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
            if not re.match(phone_pattern, v):
                raise ValueError('Invalid phone number format')
        return v


class PasswordChange(BaseModel):
    new_password: str
    new_password_repeat: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Za-z]', v) or not re.search(r'[0-9]', v):
            raise ValueError('Password must contain both letters and numbers')
        return v
    
    @validator('new_password_repeat')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Пароли не совпадают')
        return v


class AdminPasswordChange(BaseModel):
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Za-z]', v) or not re.search(r'[0-9]', v):
            raise ValueError('Password must contain both letters and numbers')
        return v


class StandardResponse(BaseModel):
    result: str
    message: Optional[str] = None
    user: Optional[UserResponse] = None
    users: Optional[list[UserResponse]] = None