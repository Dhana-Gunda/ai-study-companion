import pytest
from app.api.v1.deps import verify_project_access
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_project_isolation_invalid_id():
    with pytest.raises(HTTPException) as excinfo:
        await verify_project_access("ab")
    assert excinfo.value.status_code == 400

@pytest.mark.asyncio
async def test_project_isolation_valid_id():
    project_id = "project-123"
    result = await verify_project_access(project_id)
    assert result == project_id
