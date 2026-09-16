import jwt
import uuid
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, ValidationError
from fastapi import HTTPException

from core.config import settings


class TokenPayload(BaseModel):
    sub: str          # subject — user id, as a string per JWT spec
    exp: datetime 
    iat: datetime   # issued_at
    jti: str          # unique token ID — needed for revocation/blocklisting
    type: str        # "access" | "other" | ... - useful when more than one jwts in app


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = TokenPayload(
        sub=user_id,
        iat=now,
        exp=now+timedelta(minutes=settings.access_token_expire_minutes),
        jti=str(uuid.uuid4()),
        type="access"
    )

    return jwt.encode(payload.model_dump(), settings.jwt_secret_key, algorithm=settings.jwt_algorithm)



def decode_token(token: str) -> TokenPayload:
    raw = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    try:
        return TokenPayload(**raw)
    except ValidationError as e:
        # signature verified fine, but claims are missing/malformed — don't trust blindly
        raise HTTPException(status_code=401, detail="Malformed token claims") from e


