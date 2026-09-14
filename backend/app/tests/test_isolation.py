import pytest
from app.api.v1.deps import verify_project_ownership

def test_deps_import():
    assert callable(verify_project_ownership)

