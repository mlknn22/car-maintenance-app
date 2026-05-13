from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    DEVICE_TOKEN_PREFIX,
    decode_token,
    hash_device_token,
)
from app.crud.device import get_device_by_token_hash
from app.crud.user import get_user_by_id
from app.db.session import get_db
from app.models.device import Device
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_token(token)
    if payload is None:
        raise _CREDENTIALS_EXCEPTION

    user_id_raw = payload.get("sub")
    if user_id_raw is None:
        raise _CREDENTIALS_EXCEPTION

    try:
        user_id = int(user_id_raw)
    except (TypeError, ValueError):
        raise _CREDENTIALS_EXCEPTION

    user = await get_user_by_id(db, user_id)
    if user is None:
        raise _CREDENTIALS_EXCEPTION

    return user


async def get_current_uploader(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | Device:
    """Принимает либо device-токен (от агента), либо JWT (от веб-клиента).

    Возвращает User или Device. Роут решает, что разрешено каждому типу.
    """
    if token.startswith(DEVICE_TOKEN_PREFIX):
        device = await get_device_by_token_hash(db, hash_device_token(token))
        if device is None:
            raise _CREDENTIALS_EXCEPTION
        return device

    return await get_current_user(token=token, db=db)
