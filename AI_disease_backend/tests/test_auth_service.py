"""auth_service 单元测试。"""
import pytest

from app.schemas.user import UserCreate, UserLogin
from app.services.auth_service import AuthService
from app.utils.exceptions import AuthError


@pytest.mark.asyncio
async def test_register_success(db_init):
    payload = UserCreate(
        username="alice",
        email="alice@example.com",
        password="Password123!",
        confirm_password="Password123!",
    )
    result = await AuthService.register(payload)
    assert result.token_type == "bearer"
    assert result.access_token
    assert result.user.email == "alice@example.com"


@pytest.mark.asyncio
async def test_register_password_mismatch(db_init):
    payload = UserCreate(
        username="bob",
        email="bob@example.com",
        password="Password123!",
        confirm_password="different",
    )
    with pytest.raises(AuthError):
        await AuthService.register(payload)


@pytest.mark.asyncio
async def test_register_duplicate_email(db_init):
    payload = UserCreate(
        username="carol",
        email="carol@example.com",
        password="Password123!",
        confirm_password="Password123!",
    )
    await AuthService.register(payload)
    with pytest.raises(AuthError):
        await AuthService.register(payload)


@pytest.mark.asyncio
async def test_login_success(db_init):
    await AuthService.register(UserCreate(
        username="dave",
        email="dave@example.com",
        password="Password123!",
        confirm_password="Password123!",
    ))
    result = await AuthService.login(UserLogin(email="dave@example.com", password="Password123!"))
    assert result.user.username == "dave"


@pytest.mark.asyncio
async def test_login_wrong_password(db_init):
    await AuthService.register(UserCreate(
        username="eve",
        email="eve@example.com",
        password="Password123!",
        confirm_password="Password123!",
    ))
    with pytest.raises(AuthError):
        await AuthService.login(UserLogin(email="eve@example.com", password="wrong"))


@pytest.mark.asyncio
async def test_get_user_by_id(db_init):
    result = await AuthService.register(UserCreate(
        username="frank",
        email="frank@example.com",
        password="Password123!",
        confirm_password="Password123!",
    ))
    user = await AuthService.get_user_by_id(result.user.id)
    assert user.email == "frank@example.com"


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(db_init):
    with pytest.raises(AuthError):
        await AuthService.get_user_by_id(99999)