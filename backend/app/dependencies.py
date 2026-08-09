from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from app.services.firebase_service import FirebaseService
from app.services.gpt_service import GPTService
from app.services.tts_service import TTSService
from app.services.translation_service import TranslationService
from app.utils.jwt_utils import decode_token, is_token_blacklisted
from app.utils.logger import logger

# Reusable HTTP Bearer Security Scheme for Swagger UI Authorization
security_bearer = HTTPBearer(auto_error=True)

# Shared singleton instance of FirebaseService
_firebase_service_instance = FirebaseService()


def get_firebase_service() -> FirebaseService:
    """Dependency provider for FirebaseService."""
    return _firebase_service_instance


def get_gpt_service() -> GPTService:
    """Dependency provider for GPTService."""
    return GPTService()


def get_tts_service() -> TTSService:
    """Dependency provider for TTSService."""
    return TTSService()


def get_translation_service() -> TranslationService:
    """Dependency provider for TranslationService."""
    return TranslationService()


def get_ai_service():
    """Dependency provider for AIService."""
    from app.services.ai_service import ai_service
    return ai_service


def get_model_registry():
    """Dependency provider for ModelRegistry."""
    from app.ai.inference.model_registry import model_registry
    return model_registry


def get_model_manager():
    """Dependency provider for ModelManager."""
    from app.ai.inference.model_manager import model_manager
    return model_manager


def get_inference_engine():
    """Dependency provider for InferenceEngine."""
    from app.ai.inference.inference_engine import inference_engine
    return inference_engine


def get_accessibility_engine():
    """Dependency provider for AccessibilityEngine."""
    from app.intelligence.accessibility_engine import accessibility_engine
    return accessibility_engine




async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
    firebase_svc: FirebaseService = Depends(get_firebase_service),
) -> Dict[str, Any]:
    """
    FastAPI dependency that validates JWT access token from Bearer Authorization header
    and fetches the authenticated user's profile from Firestore.
    """
    token = credentials.credentials
    if not token:
        logger.warning("Authentication failed: Missing Authorization Bearer token.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if is_token_blacklisted(token):
        logger.warning("Authentication failed: Token has been revoked / logged out.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked or invalidated.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            logger.warning("Authentication failed: Token provided is not an access token.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type provided.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        uid = payload.get("sub")
        if not uid:
            logger.warning("Authentication failed: Token payload missing subject 'sub'.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload structure",
                headers={"WWW-Authenticate": "Bearer"},
            )

        profile = await firebase_svc.get_user_profile(uid)
        return profile

    except jwt.ExpiredSignatureError:
        logger.warning("Authentication failed: Token has expired.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as err:
        logger.warning(f"Authentication failed: Invalid token ({str(err)}).")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token signature",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Unexpected authentication failure: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
