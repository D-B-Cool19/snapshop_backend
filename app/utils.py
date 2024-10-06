from email_validator import validate_email, EmailNotValidError
from typing import Optional


def to_int(a: any, default_value: int = 0) -> int:
    try:
        return int(a)
    except (ValueError, TypeError):
        return default_value


def to_int_or_none(a: any) -> Optional[int]:
    try:
        return int(a)
    except (ValueError, TypeError):
        return None


def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False
