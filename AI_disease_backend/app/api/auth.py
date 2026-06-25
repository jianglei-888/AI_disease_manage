"""认证相关接口。"""
from fastapi import APIRouter, Depends, Request

from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService
from app.utils.ratelimit import limiter
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=Token)
@limiter.limit("10/minute")
async def register(request: Request, user_data: UserCreate):
    return await AuthService.register(user_data)


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, user_data: UserLogin):
    return await AuthService.login(user_data)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user_id: int = Depends(get_current_user)):
    user = await AuthService.get_user_by_id(current_user_id)
    return UserResponse.model_validate(user)