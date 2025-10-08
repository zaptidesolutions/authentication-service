from motor.motor_asyncio import AsyncIOMotorClient

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
auth_db = client["authentication_db"]
blacklist_collection = auth_db["token_blacklist"]  