from pathlib import Path
import warnings

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except Exception:
    pass

import pytest
from fastapi.testclient import TestClient

try:
    import main as main  # type: ignore
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import main as main  # type: ignore

try:
    from app.infrastructure.token_store import TokenStore  # type: ignore
except Exception:  # pragma: no cover
    class TokenStore:
        def __init__(self):
            self._tokens = {}

        def set_tokens(self, user_id, access_token, refresh_token=None, expiry=None):
            from types import SimpleNamespace

            self._tokens[user_id] = SimpleNamespace(
                access_token=access_token,
                refresh_token=refresh_token,
                expiry=expiry,
            )

        def get_tokens(self, user_id):
            return self._tokens.get(user_id)

warnings.filterwarnings("ignore", message="Do not expect file_or_dir in Namespace")
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*co_lnotab is deprecated.*")


@pytest.fixture
def client():
    return TestClient(main.app)


@pytest.fixture(autouse=True)
def fresh_store():
    # 重置内存型 TokenStore，避免跨测试污染
    main.store = TokenStore()
    yield
