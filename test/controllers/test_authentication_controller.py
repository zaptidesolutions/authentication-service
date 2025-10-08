import pytest
from unittest.mock import AsyncMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from controllers.authentication_controller import router as auth_router
from service.auth_service import blacklist_token

app = FastAPI()
app.include_router(auth_router)

@pytest.fixture(scope="class")
def client():
    return TestClient(app)

@pytest.mark.usefixtures("client")
class TestAuthenticationController:
    def test_login_success(self, client):
        with patch("controllers.authentication_controller.authenticate_user", new=AsyncMock(return_value={"username": "alice"})), \
             patch("controllers.authentication_controller.create_token", side_effect=lambda data, expires_delta: f"token_for_{data['sub']}"), \
             patch("controllers.authentication_controller.save_refresh_token", new=AsyncMock()):
            response = client.post("/token", data={"username": "alice", "password": "alice123"})
            assert response.status_code == 200
            json = response.json()
            assert json["access_token"].startswith("token_for_")
            assert json["refresh_token"].startswith("token_for_")
            assert json["token_type"] == "bearer"

    def test_login_failure(self, client):
        with patch("controllers.authentication_controller.authenticate_user", new=AsyncMock(return_value=None)):
            response = client.post("/token", data={"username": "alice", "password": "wrongpass"})
            assert response.status_code == 401
            assert response.json()["detail"] == "Invalid credentials"

    def test_refresh_success(self, client):
        with patch("controllers.authentication_controller.verify_refresh_token", new=AsyncMock(return_value="alice")), \
             patch("controllers.authentication_controller.create_token", side_effect=lambda data, expires_delta: f"token_for_{data['sub']}"), \
             patch("controllers.authentication_controller.save_refresh_token", new=AsyncMock()):
            response = client.post("/refresh", json={"refresh_token": "valid_refresh"})
            assert response.status_code == 200
            json = response.json()
            assert json["access_token"].startswith("token_for_")
            assert json["refresh_token"].startswith("token_for_")
            assert json["token_type"] == "bearer"

    def test_refresh_failure(self, client):
        with patch("controllers.authentication_controller.verify_refresh_token", new=AsyncMock(return_value=None)):
            response = client.post("/refresh", json={"refresh_token": "invalid_refresh"})
            assert response.status_code == 401
            assert response.json()["detail"] == "Invalid refresh token"

    def test_logout_success(self, client):
        with patch("controllers.authentication_controller.verify_refresh_token", new=AsyncMock(return_value="alice")), \
             patch("controllers.authentication_controller.save_refresh_token", new=AsyncMock()) as mock_save, \
             patch("controllers.authentication_controller.blacklist_token", new=AsyncMock()) as mock_blacklist_token:
            response = client.post("/logout", json={"access_token": "valid_access", "refresh_token": "valid_refresh", "token_type": "bearer"})
            assert response.status_code == 200
            assert response.json()["detail"] == "Logged out successfully"
            mock_save.assert_awaited_once_with("alice", None)

    def test_logout_invalid_token(self, client):
        with patch("controllers.authentication_controller.verify_refresh_token", new=AsyncMock(return_value=None)):
            response = client.post("/logout", json={"access_token": "invalid_access", "refresh_token": "invalid_refresh", "token_type": "bearer"})
            assert response.status_code == 401
            assert response.json()["detail"] == "Invalid refresh token"