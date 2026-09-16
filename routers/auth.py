from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from typing import Annotated

from core.config import settings
from models.refresh_token import RefreshToken
from security.passwords import verify_password, hash_password
from fastapi import APIRouter, Cookie, HTTPException, Response
from sqlalchemy import select, update

from db.db import SessionDep
from models.user import User
from schemas.user import UserCreate, UserLogin, UserPublic
from security.jwt import TokenResponse, create_access_token

router = APIRouter()


def _hash_refresh(raw: str):
    return hashlib.sha256(raw.encode()).hexdigest()


async def _issue_refresh_token(db, user_id) -> str:
    raw = secrets.token_urlsafe(32)
    row = RefreshToken(
        user_id=user_id,
        token_hash=_hash_refresh(raw),
        expires_at=datetime.now(timezone.utc)
        + timedelta(minutes=settings.refresh_token_expire_minutes),
    )
    db.add(row)
    await db.commit()
    return raw



@router.post("/signup", response_model=UserPublic)
async def signup(
    payload: UserCreate,
    db: SessionDep
):
    user = await db.scalar(select(User).where(User.email == payload.email))
    if user:
        raise HTTPException(409, detail="Email already exists")

    password_hash = hash_password(payload.password)

    new_user = User(email=payload.email, hashed_password=password_hash)
    db.add(new_user)
    await db.commit()

    return new_user



@router.post("/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin, db: SessionDep, response: Response):
    user = await db.scalar(select(User).where(User.email == user_credentials.email))

    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    if not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access = create_access_token(str(user.id))

    refresh = await _issue_refresh_token(db, user.id)

    response.set_cookie(
        "refresh_token",
        refresh,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 3600,
        path="/auth/refresh",
    )

    return TokenResponse(access_token=access)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    db: SessionDep,
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    if not refresh_token:
        raise HTTPException(401, detail="No refresh token")

    token_hash = _hash_refresh(refresh_token)
    row = await db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )

    if row is None:
        raise HTTPException(401, detail="Invalid refresh token")

    if row.revoked:
        raise HTTPException(401, detail="Revoked refresh token")

    if row.expires_at < datetime.now(timezone.utc):
        raise HTTPException(401, detail="Expired refresh token")

    row.revoked = True
    new_raw = await _issue_refresh_token(db, row.user_id)
    await db.commit()

    response.set_cookie(
        "refresh_token",
        new_raw,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 3600,
        path="/auth/refresh",
    )

    access = create_access_token(str(row.user_id))

    return TokenResponse(access_token=access)


@router.post("/logout")
async def logout(
    db: SessionDep,
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None
):
    if refresh_token:
        token_hash = _hash_refresh(refresh_token)
        await db.execute(update(RefreshToken).where(RefreshToken.token_hash == token_hash).values(revoked=True))
        await db.commit()
    response.delete_cookie("refresh_token", path="/auth/refresh")
    return {"detail": "Logged out"}
