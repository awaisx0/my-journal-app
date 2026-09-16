# security/deps.py
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from db.db import SessionDep
from models.user import User
from security.jwt import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: SessionDep
) -> User:
    
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired", headers={"WWW-Authenticate": "Bearer"})
    except jwt.InvalidTokenError:
        raise credentials_exc

    if payload.type != "access":
        raise credentials_exc

    user = await db.get(User, payload.sub)

    if user is None:
        raise credentials_exc

    return user
