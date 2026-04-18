import secrets

__all__ = ["generate_key"]


def generate_key() -> str:
    return secrets.token_hex(32)
