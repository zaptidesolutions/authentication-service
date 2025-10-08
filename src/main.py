from fastapi import FastAPI

# ---------------- App ----------------
api = FastAPI(title="Auth Service")

from controllers.authentication_controller import router as auth_router
from controllers.registration_controller import router as reg_router
api.include_router(auth_router)
api.include_router(reg_router)


from events import start_up  # Ensure startup events are registered

@api.on_event("startup")
async def startup_event():
    await start_up.create_default_users()