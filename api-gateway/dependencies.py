from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_superuser(user=Depends(get_current_user)):
    if not user.get("is_superuser"):
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    return user

from fastapi import HTTPException, status
from jose import jwt
from config import settings
from datetime import datetime, timedelta

def create_access_token(user_id: int, is_superuser: bool, expires_delta: timedelta = None):
    payload = {"id": user_id, "is_superuser": is_superuser}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    payload.update({"exp": expire})
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

# Пример зависимости для проверок Gateway, если понадобится
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def decode_access_token(token: str = Depends(oauth2_scheme)):
    from jose import JWTError
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload  # {"id": user_id, "is_superuser": True/False, "exp": ...}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
