from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserLoginRequest, UserRegisterRequest


class EmailAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def register(
        self,
        data: UserRegisterRequest,
    ) -> User:
        existing_user = await self.user_repository.get_by_email(
            data.email,
        )

        if existing_user is not None:
            raise EmailAlreadyExistsError

        hashed_password = hash_password(data.password)

        return await self.user_repository.create(
            email=data.email,
            password_hash=hashed_password,
            full_name=data.full_name,
        )

    async def login(
        self,
        data: UserLoginRequest,
    ) -> str:
        user = await self.user_repository.get_by_email(data.email)

        if user is None:
            raise InvalidCredentialsError

        if not verify_password(
            data.password,
            user.password_hash,
        ):
            raise InvalidCredentialsError

        if not user.is_active:
            raise InvalidCredentialsError

        return create_access_token(user.id)