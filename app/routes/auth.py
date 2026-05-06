from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.crud.user import create_user, get_user_by_email
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserResponse


router = APIRouter(prefix="/auth", tags=["Auth"])

# Pre-computed bcrypt hash used when login email doesn't exist.
# Ensures verify_password always runs once per /login request,
# making response time independent of user existence (timing-attack defence).
_DUMMY_PASSWORD_HASH = hash_password("dummy_password_for_timing_protection")


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    return await create_user(db, user_in)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_email(db, form_data.username)
    hashed = user.hashed_password if user else _DUMMY_PASSWORD_HASH
    password_ok = verify_password(form_data.password, hashed)
    if not user or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
