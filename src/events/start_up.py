from passlib.context import CryptContext
from src.config.config_setup import auth_db

# ---------------- Security Setup ----------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------- MongoDB Setup ----------------
users_collection = auth_db["users"]
roles_collection = auth_db["roles"]


# ---------------- Startup: Add default users ----------------
async def create_default_users():
    default_users = [
        {"username": "alice", "password": "alice123", "roles": ["user", "admin"]},
        {"username": "bob", "password": "bob123"},
        {"username": "superadmin", "password": "superadmin123", "roles": ["superadmin"]}  
        
    ]
    
    for user in default_users:
        existing_user = await users_collection.find_one({"username": user["username"]})
        if not existing_user:
            hashed_password = pwd_context.hash(user["password"])
            await users_collection.insert_one({"username": user["username"], "hashed_password": hashed_password})
            await roles_collection.insert_one({"username": user["username"], "role": user.get("roles", ["user"])})
            print(f"Inserted default user: {user['username']}")
        else:
            print(f"User {user['username']} already exists")