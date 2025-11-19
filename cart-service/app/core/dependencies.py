from fastapi import Request, Depends
from pydantic import BaseModel

class UserInfo(BaseModel):
    user_id: int
    username: str
    is_super: bool

def get_current_user(request: Request) -> UserInfo:
    headers = request.headers
    return UserInfo(
        user_id=int(headers["x-user-id"]),
        username=headers["x-user-name"],
        is_super=headers["x-user-issuper"] == "1"
    )
