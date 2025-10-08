from fastapi import APIRouter, HTTPException, Body
from src.service.auth_service import pwd_context, users_collection
from src.model.RegisterRequest import RegisterRequest

router = APIRouter()

@router.post("/signup")
async def register_user(request: RegisterRequest = Body(...)):
    # Check if user already exists
    existing_user = await users_collection.find_one({"username": request.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash the password and save user
    hashed_password = pwd_context.hash(request.password)
    await users_collection.insert_one({
        "username": request.username,
        "hashed_password": hashed_password
    })

    return {"message": "User registered successfully"}