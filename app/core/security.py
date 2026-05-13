import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEVICE_TOKEN_PREFIX = "cma_dev_"


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


def generate_device_token() -> tuple[str, str]:
    """Сгенерировать API-токен устройства. Возвращает (plaintext, sha256-хеш).

    Plaintext отдаётся пользователю один раз; в БД хранится только хеш.
    Префикс cma_dev_ позволяет dependency get_current_uploader быстро
    отделять device-токены от JWT.
    """
    plaintext = DEVICE_TOKEN_PREFIX + secrets.token_urlsafe(32)
    return plaintext, hash_device_token(plaintext)


def hash_device_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
