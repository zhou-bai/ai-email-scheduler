from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class TokenSet:
    access_token: str
    refresh_token: str
    expiry: Optional[datetime] = None


class TokenStore:
    def __init__(self):
        self._store: Dict[str, TokenSet] = {}

    def save_tokens(
        self,
        user_id: str,
        access_token: str,
        refresh_token: str,
        expiry: Optional[datetime] = None,
    ):
        self._store[user_id] = TokenSet(
            access_token=access_token, refresh_token=refresh_token, expiry=expiry
        )

    def get_tokens(self, user_id: str) -> Optional[TokenSet]:
        return self._store.get(user_id)

    def update_tokens(
        self,
        user_id: str,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        expiry: Optional[datetime] = None,
    ):
        current = self._store.get(user_id)
        if not current:
            return
        self._store[user_id] = TokenSet(
            access_token=access_token or current.access_token,
            refresh_token=refresh_token or current.refresh_token,
            expiry=expiry or current.expiry,
        )


_store = TokenStore()
