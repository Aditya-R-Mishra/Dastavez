"""Authentication API routes for user registration, login, and profile."""

from fastapi import APIRouter, Depends, status

from app.core.security import AuthenticatedUser, get_current_user
from app.schemas.auth import AuthTokenResponse, UserLoginRequest, UserProfileResponse, UserRegisterRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service() -> AuthService:
    """Dependency provider for AuthService."""
    return AuthService()


@router.post("/register", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthTokenResponse:
    """Register a new user account with Supabase Auth."""
    result = await auth_service.register_user(
        email=str(request.email),
        password=request.password,
        name=request.name,
    )
    return AuthTokenResponse(
        access_token=result["access_token"],
        token_type="bearer",
        user_id=result["user_id"],
        email=result["email"],
    )


@router.post("/login", response_model=AuthTokenResponse)
async def login(
    request: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthTokenResponse:
    """Authenticate user credentials and return an access token."""
    result = await auth_service.login_user(
        email=str(request.email),
        password=request.password,
    )
    return AuthTokenResponse(
        access_token=result["access_token"],
        token_type="bearer",
        user_id=result["user_id"],
        email=result["email"],
    )


@router.get("/me", response_model=UserProfileResponse)
async def get_me(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> UserProfileResponse:
    """Retrieve profile and authentication details for the current active user."""
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email or "",
        name=current_user.user_metadata.get("name"),
    )
