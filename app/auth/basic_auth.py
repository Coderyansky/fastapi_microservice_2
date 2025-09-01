from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth.password import PasswordService

security = HTTPBasic()


def authenticate_user(email: str, password: str, db: Session) -> User | None:
    """Authenticate user by email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not PasswordService.verify_password(password, user.password_hash):
        return None
    return user


def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    user = authenticate_user(credentials.username, credentials.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные логин или пароль",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


def check_user_access(current_user: User, target_user_id: int) -> bool:
    """Check if current user can access target user's data"""
    return current_user.id == target_user_id