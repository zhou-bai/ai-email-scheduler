import pytest
from fastapi.testclient import TestClient

import backend.main as main
from backend.infrastructure.token_store import TokenStore

import warnings
warnings.filterwarnings("ignore", message="Do not expect file_or_dir in Namespace")

@pytest.fixture
def client():
    return TestClient(main.app)


@pytest.fixture(autouse=True)
def fresh_store():
    # 重置内存型 TokenStore，避免跨测试污染
    main.store = TokenStore()
    yield