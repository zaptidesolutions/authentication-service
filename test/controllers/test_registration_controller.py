from unittest.mock import AsyncMock, Mock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from controllers.registration_controller import router as reg_router

app = FastAPI()
app.include_router(reg_router)

def test_register_user_success():
    with patch("controllers.registration_controller.users_collection", new=AsyncMock()) as mock_users, \
         patch("controllers.registration_controller.pwd_context", new=Mock()) as mock_pwd:
        mock_users.find_one.return_value = None
        mock_pwd.hash.return_value = "hashed_pw"
        async def insert_one_side_effect(doc):
            return None
        mock_users.insert_one.side_effect = insert_one_side_effect

        client = TestClient(app)
        response = client.post("/signup", json={"username": "alice", "password": "alice123"})
        assert response.status_code == 200
        assert response.json()["message"] == "User registered successfully"
        assert mock_users.insert_one.call_args[0][0] == {
            "username": "alice",
            "hashed_password": "hashed_pw"
        }

def test_register_user_existing():
    with patch("controllers.registration_controller.users_collection", new=AsyncMock()) as mock_users, \
         patch("controllers.registration_controller.pwd_context", new=AsyncMock()):
        mock_users.find_one.return_value = {"username": "alice", "hashed_password": "hashed_pw"}

        client = TestClient(app)
        response = client.post("/signup", json={"username": "alice", "password": "alice123"})
        assert response.status_code == 400
        assert response.json()["detail"] == "Username already exists"