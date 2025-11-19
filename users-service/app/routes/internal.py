# user-service/routers/internal.py
from fastapi import APIRouter, Depends, Header, HTTPException, status
from jose import jwt, JWTError
from ..core.config import settings
from ..core.dependencies import oauth2_scheme 

router = APIRouter(prefix="/internal", tags=["internal"])

@router.get("/verify_token")
async def verify_token(authorization: str = Header(...)):
    """
    Проверяет JWT и возвращает данные пользователя.
    Используется другими сервисами.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth header")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("id")
        username = payload.get("username")
        is_superuser = payload.get("is_superuser")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return {"id": user_id, "username": username, "is_superuser": is_superuser}
