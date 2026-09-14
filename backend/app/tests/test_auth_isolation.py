import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token
)
from app.models.db_models import User, Project
from app.api.v1.deps import verify_project_ownership

def test_password_hashing():
    raw_password = "securePassword123!"
    hashed = get_password_hash(raw_password)
    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("wrongPassword", hashed) is False

def test_jwt_token_generation_and_decoding():
    payload_data = {"sub": "user-12345", "email": "test@studycompanion.ai", "role": "user"}
    token = create_access_token(payload_data)
    assert isinstance(token, str)
    assert len(token) > 20

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user-12345"
    assert decoded["email"] == "test@studycompanion.ai"
    assert decoded["role"] == "user"

@pytest.mark.asyncio
async def test_verify_project_ownership_allowed_for_owner():
    user_a = User(id="user-a", email="a@example.com", name="User A", role="user")
    project = Project(id="proj-1", user_id="user-a", name="User A Project", space_id="space-1", learning_goal="Goal")

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = project
    mock_db.execute.return_value = mock_result

    result = await verify_project_ownership("proj-1", current_user=user_a, db=mock_db)
    assert result.id == "proj-1"
    assert result.user_id == "user-a"

@pytest.mark.asyncio
async def test_verify_project_ownership_rejected_for_cross_tenant_user():
    user_b = User(id="user-b", email="b@example.com", name="User B", role="user")
    project_of_user_a = Project(id="proj-1", user_id="user-a", name="User A Project", space_id="space-1", learning_goal="Goal")

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = project_of_user_a
    mock_db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await verify_project_ownership("proj-1", current_user=user_b, db=mock_db)

    assert exc_info.value.status_code == 403
    assert "Access forbidden" in exc_info.value.detail

@pytest.mark.asyncio
async def test_verify_project_ownership_allowed_for_admin():
    admin = User(id="admin-1", email="admin@example.com", name="Admin", role="admin")
    project_of_user_a = Project(id="proj-1", user_id="user-a", name="User A Project", space_id="space-1", learning_goal="Goal")

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = project_of_user_a
    mock_db.execute.return_value = mock_result

    result = await verify_project_ownership("proj-1", current_user=admin, db=mock_db)
    assert result.id == "proj-1"

@pytest.mark.asyncio
async def test_verify_project_ownership_not_found():
    user_a = User(id="user-a", email="a@example.com", name="User A", role="user")

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await verify_project_ownership("nonexistent-proj", current_user=user_a, db=mock_db)

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()
