import pytest
from unittest.mock import AsyncMock, patch
from datetime import timedelta, datetime
from jose import jwt

from service import auth_service

@pytest.fixture
def mock_users_collection():
    mock = AsyncMock()
    return mock

@pytest.fixture
def mock_refresh_collection():
    mock = AsyncMock()
    return mock

@pytest.fixture
def mock_pwd_context():
    mock = AsyncMock()
    mock.verify.return_value = True
    return mock

def test_create_token_and_decode():
    data = {"sub": "alice"}
    expires = timedelta(minutes=5)
    token = auth_service.create_token(data, expires)
    decoded = jwt.decode(token, auth_service.SECRET_KEY, algorithms=[auth_service.ALGORITHM])
    assert decoded["sub"] == "alice"
    assert "exp" in decoded

@pytest.mark.asyncio
async def test_authenticate_user_success(monkeypatch):
    user = {"username": "alice", "hashed_password": "hashed"}
    monkeypatch.setattr(auth_service, "get_user", AsyncMock(return_value=user))
    monkeypatch.setattr(auth_service.pwd_context, "verify", lambda p, h: True)
    result = await auth_service.authenticate_user("alice", "password")
    assert result == user

@pytest.mark.asyncio
async def test_authenticate_user_failure(monkeypatch):
    monkeypatch.setattr(auth_service, "get_user", AsyncMock(return_value=None))
    result = await auth_service.authenticate_user("bob", "password")
    assert result is None

@pytest.mark.asyncio
async def test_save_refresh_token():
    mock_refresh = AsyncMock()
    with patch("service.auth_service.refresh_collection", new=mock_refresh):
        await auth_service.save_refresh_token("alice", "token")
        mock_refresh.update_one.assert_awaited_once()

@pytest.mark.asyncio
async def test_verify_refresh_token_success(monkeypatch):
    username = "alice"
    token = auth_service.create_token({"sub": username}, timedelta(minutes=5))
    monkeypatch.setattr(auth_service.refresh_collection, "find_one", AsyncMock(return_value={"username": username, "refresh_token": token}))
    result = await auth_service.verify_refresh_token(token)
    assert result == username

@pytest.mark.asyncio
async def test_verify_refresh_token_invalid_token(monkeypatch):
    monkeypatch.setattr(auth_service.refresh_collection, "find_one", AsyncMock(return_value=None))
    result = await auth_service.verify_refresh_token("invalid_token")
    assert result is None

@pytest.mark.asyncio
async def test_verify_refresh_token_no_username(monkeypatch):
    # Create a token without "sub" field
    from service.auth_service import SECRET_KEY, ALGORITHM
    from jose import jwt
    token = jwt.encode({"exp": datetime.utcnow()}, SECRET_KEY, algorithm=ALGORITHM)
    # Patch find_one to not be called (since username is missing)
    monkeypatch.setattr(auth_service.refresh_collection, "find_one", AsyncMock())
    result = await auth_service.verify_refresh_token(token)
    assert result is None

@pytest.mark.asyncio
async def test_get_user_success(monkeypatch):
    expected_user = {"username": "alice", "hashed_password": "hashed_pw"}
    mock_collection = AsyncMock()
    mock_collection.find_one.return_value = expected_user
    monkeypatch.setattr(auth_service, "users_collection", mock_collection)
    result = await auth_service.get_user("alice")
    assert result == expected_user

@pytest.mark.asyncio
async def test_verify_refresh_token_token_doc_none(monkeypatch):
    # token_doc is None
    username = "alice"
    token = auth_service.create_token({"sub": username}, timedelta(minutes=5))
    monkeypatch.setattr(auth_service.refresh_collection, "find_one", AsyncMock(return_value=None))
    result = await auth_service.verify_refresh_token(token)
    assert result is None

@pytest.mark.asyncio
async def test_verify_refresh_token_refresh_token_mismatch(monkeypatch):
    # token_doc["refresh_token"] != refresh_token
    username = "alice"
    token = auth_service.create_token({"sub": username}, timedelta(minutes=5))
    monkeypatch.setattr(auth_service.refresh_collection, "find_one", AsyncMock(return_value={"username": username, "refresh_token": "other_token"}))
    result = await auth_service.verify_refresh_token(token)
    assert result is None