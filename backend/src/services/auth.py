"""
Authentication service for Apple Sign In and JWT token management.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
import httpx
from jwt import PyJWKClient

from src.core.config import settings


# Apple's public keys endpoint
APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"

# Cache for Apple's public keys
_apple_jwk_client: PyJWKClient | None = None


def get_apple_jwk_client() -> PyJWKClient:
    """Get or create Apple's JWK client for token verification."""
    global _apple_jwk_client
    if _apple_jwk_client is None:
        _apple_jwk_client = PyJWKClient(APPLE_KEYS_URL)
    return _apple_jwk_client


async def verify_apple_identity_token(identity_token: str) -> dict[str, Any] | None:
    """
    Verify Apple's identity token and return the decoded payload.

    Args:
        identity_token: The JWT identity token from Sign in with Apple

    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        # Get Apple's public keys
        jwk_client = get_apple_jwk_client()
        signing_key = jwk_client.get_signing_key_from_jwt(identity_token)

        # Decode and verify the token
        decoded = jwt.decode(
            identity_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.apple_client_id,
            issuer="https://appleid.apple.com",
        )

        return decoded
    except jwt.ExpiredSignatureError:
        print("[Auth] Apple identity token has expired")
        return None
    except jwt.InvalidAudienceError:
        print("[Auth] Apple identity token has invalid audience")
        return None
    except jwt.InvalidIssuerError:
        print("[Auth] Apple identity token has invalid issuer")
        return None
    except Exception as e:
        print(f"[Auth] Failed to verify Apple identity token: {e}")
        # In development, allow skipping verification
        if settings.app_env == "development":
            print("[Auth] Development mode: skipping Apple token verification")
            # Return minimal payload for development
            return {"sub": "dev_user"}
        return None


def create_access_token(user_id: str, extra_claims: dict | None = None) -> str:
    """
    Create a JWT access token for a user.

    Args:
        user_id: The user's ID
        extra_claims: Additional claims to include in the token

    Returns:
        Encoded JWT token
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    payload = {
        "sub": user_id,
        "iat": now,
        "exp": expire,
        "type": "access",
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str) -> str:
    """
    Create a JWT refresh token for a user.

    Args:
        user_id: The user's ID

    Returns:
        Encoded JWT refresh token
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.jwt_refresh_token_expire_days)

    payload = {
        "sub": user_id,
        "iat": now,
        "exp": expire,
        "type": "refresh",
    }

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_token(token: str, token_type: str = "access") -> dict[str, Any] | None:
    """
    Verify a JWT token and return the decoded payload.

    Args:
        token: The JWT token to verify
        token_type: Expected token type ("access" or "refresh")

    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        if payload.get("type") != token_type:
            print(f"[Auth] Invalid token type: expected {token_type}, got {payload.get('type')}")
            return None

        return payload
    except jwt.ExpiredSignatureError:
        print("[Auth] Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"[Auth] Invalid token: {e}")
        return None


def get_user_id_from_token(token: str) -> str | None:
    """
    Extract user ID from a valid access token.

    Args:
        token: The JWT access token

    Returns:
        User ID if token is valid, None otherwise
    """
    payload = verify_token(token, "access")
    if payload:
        return payload.get("sub")
    return None
