from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
from models.user import User
from config.settings import settings
from typing import Optional


async def get_current_user(request: Request) -> User:
    """
    Dependency to get current authenticated user from JWT cookie
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized, no token",
    )
    
    # Get JWT from cookie
    token = request.cookies.get("jwt")
    
    if not token:
        raise credentials_exception
    
    try:
        # Decode JWT
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("userId")
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized, token failed",
        )
    
    # Get user from database
    user = await User.get(user_id)
    
    if user is None:
        raise credentials_exception
    
    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to check if user is admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized as an admin",
        )
    return current_user


# Optional dependency for routes that may or may not require auth
async def get_current_user_optional(request: Request) -> Optional[User]:
    """
    Dependency to get current user if authenticated, None otherwise
    """
    token = request.cookies.get("jwt")
    
    if not token:
        return None
    
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("userId")
        
        if user_id is None:
            return None
            
        user = await User.get(user_id)
        return user
        
    except JWTError:
        return None
