from service.auth_service import (
    authenticate_user,
    blacklist_token,
    create_token,
    save_refresh_token,
    verify_refresh_token
)
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from model.Token import Token
from model.RefreshRequest import RefreshRequest
from config.config_setup import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)

from fastapi import APIRouter

router = APIRouter()
# ---------------- Auth Endpoints ----------------
@router.post("/login", response_model=Token)
@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_token(
        data={"sub": user["username"]}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_token(
        data={"sub": user["username"]}, 
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    await save_refresh_token(user["username"], refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_tokens(refresh_request: RefreshRequest):
    username = await verify_refresh_token(refresh_request.refresh_token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_token(
        data={"sub": username}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    new_refresh_token = create_token(
        data={"sub": username}, 
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    # Rotate refresh token (old one becomes invalid)
    await save_refresh_token(username, new_refresh_token)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(token: Token):
    username = await verify_refresh_token(token.refresh_token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Invalidate the refresh token
    await save_refresh_token(username, None)
    await blacklist_token(token.access_token)
    return {"detail": "Logged out successfully"}