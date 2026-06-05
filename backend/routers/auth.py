from fastapi import APIRouter, HTTPException

from schemas.auth import LoginRequest, LoginResponse


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    if payload.username == "admin" and payload.password == "admin123":
        return LoginResponse(username="admin", token="demo-admin-token")
    raise HTTPException(status_code=401, detail="账号或密码错误")
