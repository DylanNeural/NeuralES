"""Token JWT partagé entre toutes les pages."""
_token: str | None = None


def set_token(t: str) -> None:
    global _token
    _token = t


def get_token() -> str | None:
    return _token


def auth_header() -> dict:
    return {"Authorization": f"Bearer {_token}"} if _token else {}
