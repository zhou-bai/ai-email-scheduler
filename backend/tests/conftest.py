import warnings

import pytest
from fastapi.testclient import TestClient

import main as main
from app.infrastructure.token_store import TokenStore

warnings.filterwarnings("ignore", message="Do not expect file_or_dir in Namespace")


@pytest.fixture
def client():
    return TestClient(main.app)


@pytest.fixture(autouse=True)
def fresh_store():
    # 重置内存型 TokenStore，避免跨测试污染
    main.store = TokenStore()
    yield
