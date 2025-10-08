from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

# Import Config and DB
from config.config_setup import (
    SECRET_KEY,
    ALGORITHM,
    auth_db,
    blacklist_collection
)

# ---------------- Security Setup ----------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ---------------- MongoDB Setup ----------------
users_collection = auth_db["users"]
refresh_collection = auth_db["refresh_tokens"]

# ---------------- Helper Functions ----------------
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def get_user(username: str):
    return await users_collection.find_one({"username": username})

async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def save_refresh_token(username: str, refresh_token: str):
    await refresh_collection.update_one(
        {"username": username},
        {"$set": {"refresh_token": refresh_token, "created_at": datetime.utcnow()}},
        upsert=True
    )

async def verify_refresh_token(refresh_token: str) -> Optional[str]:
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            return None

        # Check in DB if this refresh token is still valid
        token_doc = await refresh_collection.find_one({"username": username})
        if not token_doc or token_doc["refresh_token"] != refresh_token:
            return None

        return username
    except JWTError:
        return None

async def blacklist_token(token: str):
    await blacklist_collection.insert_one({
        "token": token,
        "revoked_at": datetime.utcnow()
    })
