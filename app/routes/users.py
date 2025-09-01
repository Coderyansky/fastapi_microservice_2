from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate, UserResponse, UserProfileUpdate, 
    PasswordChange, AdminPasswordChange, StandardResponse
)
from app.auth.basic_auth import get_current_user, check_user_access
from app.auth.password import PasswordService

router = APIRouter()


@router.get("/users", response_model=StandardResponse)
def get_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of all users"""
    users = db.query(User).all()
    return StandardResponse(
        result="ok",
        users=[UserResponse.from_orm(user) for user in users]
    )


@router.post("/users", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email уже используется"
            )
        
        # Create new user
        hashed_password = PasswordService.hash_password(user_data.password)
        db_user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=hashed_password,
            phone=user_data.phone
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return StandardResponse(
            result="ok",
            user=UserResponse.from_orm(db_user)
        )
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email уже используется"
        )


@router.get("/users/{user_id}", response_model=StandardResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user information by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return StandardResponse(
        result="ok",
        user=UserResponse.from_orm(user)
    )


@router.delete("/users/{user_id}", response_model=StandardResponse)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user by ID (only own profile)"""
    if not check_user_access(current_user, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    db.delete(user)
    db.commit()
    
    return StandardResponse(
        result="ok",
        message="Пользователь успешно удален"
    )


@router.put("/api/user/profile", response_model=StandardResponse)
def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update own profile data"""
    try:
        # Check if email is being changed and if it already exists
        if profile_data.email and profile_data.email != current_user.email:
            existing_user = db.query(User).filter(User.email == profile_data.email).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email уже используется"
                )
        
        # Update fields if provided
        if profile_data.name is not None:
            current_user.name = profile_data.name
        if profile_data.email is not None:
            current_user.email = profile_data.email
        if profile_data.phone is not None:
            current_user.phone = profile_data.phone
        
        db.commit()
        db.refresh(current_user)
        
        return StandardResponse(
            result="ok",
            user=UserResponse.from_orm(current_user)
        )
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email уже используется"
        )


@router.put("/api/user/password", response_model=StandardResponse)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change own password"""
    # Hash and save new password
    hashed_password = PasswordService.hash_password(password_data.new_password)
    current_user.password_hash = hashed_password
    
    db.commit()
    
    return StandardResponse(
        result="ok",
        message="Пароль успешно изменён"
    )


@router.post("/users/{user_id}/change-password", response_model=StandardResponse)
def admin_change_password(
    user_id: int,
    password_data: AdminPasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password by ID (administrative function)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Hash and save new password
    hashed_password = PasswordService.hash_password(password_data.new_password)
    user.password_hash = hashed_password
    
    db.commit()
    
    return StandardResponse(
        result="ok",
        message="Пароль пользователя успешно изменён"
    )