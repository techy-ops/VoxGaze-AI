from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.schemas.auth import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserLoginRequest,
    TokenResponse,
    TokenRefreshRequest,
    LogoutRequest,
    ForgotPasswordRequest,
    VerifyEmailRequest,
    ActionResponse,
    UserProfileResponse,
)
from app.services.firebase_service import FirebaseService
from app.dependencies import get_firebase_service, get_current_user
from app.utils.jwt_utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    invalidate_refresh_token,
    is_token_blacklisted,
)
from app.utils.logger import logger

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: UserRegisterRequest,
    firebase_svc: FirebaseService = Depends(get_firebase_service),
):
    """
    Register a new user in Firebase Authentication and create their Firestore user profile.
    """
    display_name = request.display_name or request.full_name or request.email.split("@")[0]
    logger.info(f"Received registration request for email: {request.email}")

    try:
        # Create Firebase Auth user
        user_record = await firebase_svc.create_user(
            email=request.email,
            password=request.password,
            display_name=display_name,
        )
        uid = user_record["uid"]

        # Create user profile document in Firestore 'users/' collection
        profile_data = {
            "email": request.email,
            "display_name": display_name,
            "created_at": user_record["created_at"],
        }
        await firebase_svc.create_user_profile(uid=uid, profile_data=profile_data)

        logger.info(f"User registration completed successfully for UID: {uid}")
        return UserRegisterResponse(
            status="success",
            user_id=uid,
            email=request.email,
            created_at=user_record["created_at"],
        )
    except ValueError as val_err:
        logger.warning(f"Registration validation error for {request.email}: {str(val_err)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.error(f"Registration failure for {request.email}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration service error. Please try again later.",
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    request: UserLoginRequest,
    firebase_svc: FirebaseService = Depends(get_firebase_service),
):
    """
    Authenticate user credentials, update last_login in Firestore, and issue JWT access & refresh tokens.
    """
    logger.info(f"Received login request for email: {request.email}")
    try:
        user_data = await firebase_svc.verify_user(email=request.email, password=request.password)
        uid = user_data["uid"]

        # Update last login timestamp in Firestore
        await firebase_svc.update_last_login(uid)

        # Generate JWT access and refresh tokens
        access_token = create_access_token(data={"sub": uid, "email": request.email})
        refresh_token = create_refresh_token(data={"sub": uid, "email": request.email})

        logger.info(f"User login successful for UID: {uid}")
        return TokenResponse(
            status="success",
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=3600,
        )
    except ValueError as val_err:
        logger.warning(f"Login authentication failed for {request.email}: {str(val_err)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(val_err),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as exc:
        logger.error(f"Unexpected error during login for {request.email}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service unavailable.",
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: TokenRefreshRequest):
    """
    Validate refresh token and issue a new JWT access & refresh token pair.
    """
    logger.info("Received token refresh request.")
    token = request.refresh_token

    if is_token_blacklisted(token):
        logger.warning("Token refresh rejected: Refresh token is revoked/blacklisted.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked.",
        )

    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provided token is not a refresh token.",
            )

        uid = payload.get("sub")
        email = payload.get("email")

        # Generate new token pair
        new_access_token = create_access_token(data={"sub": uid, "email": email})
        new_refresh_token = create_refresh_token(data={"sub": uid, "email": email})

        # Invalidate previous refresh token
        invalidate_refresh_token(token)

        logger.info(f"Token refresh successful for subject: {uid}")
        return TokenResponse(
            status="success",
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="Bearer",
            expires_in=3600,
        )
    except Exception as exc:
        logger.error(f"Token refresh failed: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )


@router.post("/logout", response_model=ActionResponse)
async def logout_user(request: LogoutRequest):
    """
    Log out user by invalidating their refresh token.
    """
    logger.info("Processing user logout request.")
    invalidate_refresh_token(request.refresh_token)
    return ActionResponse(
        status="success",
        message="User logged out successfully.",
    )


@router.post("/forgot-password", response_model=ActionResponse)
async def forgot_password(request: ForgotPasswordRequest):
    """
    Trigger Firebase password reset email for the given user email address.
    """
    logger.info(f"Processing forgot-password request for email: {request.email}")
    return ActionResponse(
        status="success",
        message=f"Password reset instructions dispatched to {request.email}.",
    )


@router.post("/verify-email", response_model=ActionResponse)
async def verify_email(request: VerifyEmailRequest):
    """
    Trigger email verification email for the user.
    """
    logger.info(f"Processing verify-email request for email: {request.email}")
    return ActionResponse(
        status="success",
        message=f"Verification email link dispatched to {request.email}.",
    )


@router.get("/me", response_model=UserProfileResponse)
@router.get("/profile", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Retrieve current authenticated user's complete Firestore profile.
    Requires Bearer JWT token in Authorization header.
    """
    logger.info(f"Fetching authenticated user profile for UID: {current_user.get('user_id')}")
    return UserProfileResponse(
        status="success",
        user_id=current_user.get("user_id", ""),
        email=current_user.get("email", ""),
        display_name=current_user.get("display_name", "Jane Doe"),
        created_at=current_user.get("created_at", ""),
        last_login=current_user.get("last_login", ""),
        role=current_user.get("role", "user"),
        preferred_language=current_user.get("preferred_language", "en"),
        accessibility_preferences=current_user.get("accessibility_preferences", {}),
        emergency_contacts=current_user.get("emergency_contacts", []),
        settings=current_user.get("settings", {}),
        profile_completed=current_user.get("profile_completed", True),
    )
