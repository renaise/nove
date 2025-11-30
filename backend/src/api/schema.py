from datetime import datetime
from enum import Enum

import strawberry


@strawberry.enum
class TryOnStatusGQL(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@strawberry.type
class DressType:
    id: str
    name: str
    description: str | None
    image_url: str
    thumbnail_url: str | None
    style: str | None
    designer: str | None
    is_active: bool
    created_at: datetime


@strawberry.type
class TryOnRequestType:
    id: str
    person_image_url: str
    dress_id: str
    status: TryOnStatusGQL
    result_image_url: str | None
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None


@strawberry.input
class CreateTryOnInput:
    person_image_base64: str
    dress_id: str
    user_id: str | None = None


@strawberry.type
class CreateTryOnResult:
    id: str
    status: TryOnStatusGQL
    message: str


# Authentication Types
@strawberry.type
class UserType:
    id: str
    email: str | None
    name: str | None
    apple_user_id: str | None
    created_at: datetime
    updated_at: datetime


@strawberry.type
class AuthResult:
    user: UserType
    token: str
    refresh_token: str


@strawberry.input
class AppleAuthInput:
    identity_token: str | None
    authorization_code: str | None
    user_identifier: str
    email: str | None = None
    given_name: str | None = None
    family_name: str | None = None


@strawberry.input
class RefreshTokenInput:
    refresh_token: str
