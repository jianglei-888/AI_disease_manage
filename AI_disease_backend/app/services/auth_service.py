"""认证服务：注册 / 登录 / 取当前用户。"""
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.utils.exceptions import AuthError
from app.utils.logger import get_logger
from app.utils.security import create_access_token, get_password_hash, verify_password

logger = get_logger(__name__)


class AuthService:
    @staticmethod
    async def register(user_data: UserCreate) -> Token:
        if await User.filter(email=user_data.email).exists():
            raise AuthError("该邮箱已被注册")

        if user_data.password != user_data.confirm_password:
            raise AuthError("两次输入的密码不一致")

        user = await User.create(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
        )
        token = create_access_token({"sub": str(user.id)})
        logger.info("用户注册成功：user_id=%s email=%s", user.id, user.email)
        return Token(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    async def login(user_data: UserLogin) -> Token:
        user = await User.filter(email=user_data.email).first()
        if not user or not verify_password(user_data.password, user.password_hash):
            raise AuthError("邮箱或密码错误")

        token = create_access_token({"sub": str(user.id)})
        logger.info("用户登录：user_id=%s email=%s", user.id, user.email)
        return Token(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    async def get_user_by_id(user_id: int) -> User:
        user = await User.filter(id=user_id).first()
        if not user:
            raise AuthError("用户不存在")
        return user