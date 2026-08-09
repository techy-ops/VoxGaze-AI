from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import jwt
from app.config import settings
from app.utils.logger import logger

# In-memory revoked/invalidated refresh token set
BLACK_LISTED_REFRESH_TOKENS = set()


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate a signed JWT access token.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": now,
        "type": "access",
    })
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    logger.info(f"Generated JWT access token for subject: {data.get('sub')}")
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate a signed JWT refresh token.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": now,
        "type": "refresh",
    })
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    logger.info(f"Generated JWT refresh token for subject: {data.get('sub')}")
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT access or refresh token.
    Raises jwt.PyJWTError on failure or expiration.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT validation failed: Token has expired")
        raise
    except jwt.InvalidTokenError as err:
        logger.warning(f"JWT validation failed: Invalid token ({str(err)})")
        raise


def invalidate_refresh_token(token: str) -> None:
    """
    Invalidate/Blacklist a refresh token on logout.
    """
    BLACK_LISTED_REFRESH_TOKENS.add(token)
    logger.info("Refresh token successfully invalidated on logout")


def is_token_blacklisted(token: str) -> bool:
    """
    Check whether a refresh token has been invalidated.
    """
    return token in BLACK_LISTED_REFRESH_TOKENS
