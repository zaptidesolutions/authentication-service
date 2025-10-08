from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

import main

def test_app_title():
    assert main.api.title == "Auth Service"

def test_router_included():
    # Check that the authentication router is included
    routes = [route.path for route in main.api.routes]
    assert "/token" in routes
    assert "/refresh" in routes

def test_registration_router_included():
    # Check that the registration router is included
    routes = [route.path for route in main.api.routes]
    assert "/signup" in routes

def test_startup_event_called(monkeypatch):
    mock_create_default_users = AsyncMock()
    monkeypatch.setattr(main.start_up, "create_default_users", mock_create_default_users)

    # Simulate FastAPI startup event
    with TestClient(main.api) as client:
        pass  # Startup event runs automatically

    mock_create_default_users.assert_awaited_once()