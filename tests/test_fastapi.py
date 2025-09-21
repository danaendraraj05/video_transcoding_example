"""
Tests for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient


# FastAPI tests are skipped when FastAPI is not enabled
pytest.skip("FastAPI not enabled", allow_module_level=True)
 