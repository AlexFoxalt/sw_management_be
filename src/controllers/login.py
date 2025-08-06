from datetime import UTC, datetime, timedelta
from hashlib import sha256

import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from settings import Settings
from src.exceptions import ServiceForbidden
from src.repositories.users import UserRepo


class LoginController:
    def __init__(self, settings: Settings, users: UserRepo) -> None:
        self._settings = settings
        self._users = users

    async def login(self, session: AsyncSession, username: str, password: str) -> dict:
        user = await self._users.get_by_username(session, username)
        if not user:
            raise ServiceForbidden("Incorrect username or password")

        hashed_pass = sha256(password.encode()).hexdigest()
        if hashed_pass != user.password:
            raise ServiceForbidden("Incorrect username or password")
        token = self._create_jwt_token(
            {
                "username": user.username,
                "user_id": user.user_id,
                "role": user.role.value,
                "full_name": user.full_name,
            }
        )
        return {"token": token, "refreshToken": ""}

    def _create_jwt_token(self, data: dict, expires_delta: timedelta = timedelta(hours=1)):
        to_encode = data.copy()
        expire = datetime.now(UTC) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, self._settings.jwt_secret, algorithm=self._settings.jwt_algorithm
        )
        return encoded_jwt
