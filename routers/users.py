from fastapi import APIRouter, Depends, HTTPException, status, Response
from models.user import User
from schemas.user import (
    UserLogin, UserRegister, UserUpdate, UserAdminUpdate,
    UserResponse, UserListResponse
)
from middleware.auth import get_current_user, require_admin
from utils.generate_token import generate_token
from typing import List
from bson import ObjectId

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/auth", response_model=UserResponse)
async def auth_user(user_data: UserLogin, response: Response):
    """Authenticate user & get token"""
    user = await User.find_one(User.email == user_data.email)
    
    if user and user.verify_password(user_data.password):
        generate_token(response, str(user.id))
        
        return UserResponse(
            _id=str(user.id),
            name=user.name,
            email=user.email,
            isAdmin=user.is_admin
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister, response: Response):
    """Register a new user"""
    user_exists = await User.find_one(User.email == user_data.email)
    
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    user = User(
        name=user_data.name,
        email=user_data.email,
        password=user_data.password
    )
    
    await user.save()
    
    generate_token(response, str(user.id))
    
    return UserResponse(
        _id=str(user.id),
        name=user.name,
        email=user.email,
        isAdmin=user.is_admin
    )


@router.post("/logout")
async def logout_user(response: Response):
    """Logout user / clear cookie"""
    response.delete_cookie("jwt")
    return {"message": "Logged out successfully"}


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get user profile"""
    return UserResponse(
        _id=str(current_user.id),
        name=current_user.name,
        email=current_user.email,
        isAdmin=current_user.is_admin
    )


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update user profile"""
    if user_data.name:
        current_user.name = user_data.name
    if user_data.email:
        current_user.email = user_data.email
    if user_data.password:
        current_user.password = user_data.password
    
    await current_user.save()
    
    return UserResponse(
        _id=str(current_user.id),
        name=current_user.name,
        email=current_user.email,
        isAdmin=current_user.is_admin
    )


@router.get("", response_model=List[UserListResponse])
async def get_users(admin_user: User = Depends(require_admin)):
    """Get all users (Admin only)"""
    users = await User.find_all().to_list()
    
    return [
        UserListResponse(
            _id=str(user.id),
            name=user.name,
            email=user.email,
            isAdmin=user.is_admin,
            createdAt=user.created_at
        )
        for user in users
    ]


@router.delete("/{user_id}")
async def delete_user(user_id: str, admin_user: User = Depends(require_admin)):
    """Delete user (Admin only)"""
    try:
        user = await User.get(ObjectId(user_id))
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete admin user"
        )
    
    await user.delete()
    
    return {"message": "User removed"}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str, admin_user: User = Depends(require_admin)):
    """Get user by ID (Admin only)"""
    try:
        user = await User.get(ObjectId(user_id))
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        _id=str(user.id),
        name=user.name,
        email=user.email,
        isAdmin=user.is_admin
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserAdminUpdate,
    admin_user: User = Depends(require_admin)
):
    """Update user (Admin only)"""
    try:
        user = await User.get(ObjectId(user_id))
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user_data.name:
        user.name = user_data.name
    if user_data.email:
        user.email = user_data.email
    if user_data.is_admin is not None:
        user.is_admin = user_data.is_admin
    
    await user.save()
    
    return UserResponse(
        _id=str(user.id),
        name=user.name,
        email=user.email,
        isAdmin=user.is_admin
    )
