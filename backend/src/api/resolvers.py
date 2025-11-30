from datetime import datetime, timezone
from uuid import uuid4

import strawberry
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schema import (
    AppleAuthInput,
    AuthResult,
    CreateTryOnInput,
    CreateTryOnResult,
    DressType,
    RefreshTokenInput,
    TryOnRequestType,
    TryOnStatusGQL,
    UserType,
)
from src.core.database import async_session_maker
from src.core.config import settings
from src.models.dress import Dress
from src.models.try_on import TryOnRequest, TryOnStatus
from src.models.user import User
from src.services.auth import (
    create_access_token,
    create_refresh_token,
    verify_apple_identity_token,
    verify_token,
)
from src.temporal.client import get_temporal_client
from src.temporal.workflows import TryOnWorkflow, TryOnWorkflowInput


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        return session


@strawberry.type
class Query:
    @strawberry.field
    async def dresses(self, active_only: bool = True) -> list[DressType]:
        async with async_session_maker() as session:
            query = select(Dress)
            if active_only:
                query = query.where(Dress.is_active == True)  # noqa: E712
            result = await session.execute(query)
            dresses = result.scalars().all()
            return [
                DressType(
                    id=d.id,
                    name=d.name,
                    description=d.description,
                    image_url=d.image_url,
                    thumbnail_url=d.thumbnail_url,
                    style=d.style,
                    designer=d.designer,
                    is_active=d.is_active,
                    created_at=d.created_at,
                )
                for d in dresses
            ]

    @strawberry.field
    async def dress(self, id: str) -> DressType | None:
        async with async_session_maker() as session:
            result = await session.execute(select(Dress).where(Dress.id == id))
            d = result.scalar_one_or_none()
            if not d:
                return None
            return DressType(
                id=d.id,
                name=d.name,
                description=d.description,
                image_url=d.image_url,
                thumbnail_url=d.thumbnail_url,
                style=d.style,
                designer=d.designer,
                is_active=d.is_active,
                created_at=d.created_at,
            )

    @strawberry.field
    async def try_on_request(self, id: str) -> TryOnRequestType | None:
        async with async_session_maker() as session:
            result = await session.execute(
                select(TryOnRequest).where(TryOnRequest.id == id)
            )
            req = result.scalar_one_or_none()
            if not req:
                return None
            return TryOnRequestType(
                id=req.id,
                person_image_url=req.person_image_url,
                dress_id=req.dress_id,
                status=TryOnStatusGQL(req.status.value),
                result_image_url=req.result_image_url,
                error_message=req.error_message,
                created_at=req.created_at,
                completed_at=req.completed_at,
            )

    @strawberry.field
    async def my_try_on_requests(self, user_id: str) -> list[TryOnRequestType]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(TryOnRequest)
                .where(TryOnRequest.user_id == user_id)
                .order_by(TryOnRequest.created_at.desc())
            )
            requests = result.scalars().all()
            return [
                TryOnRequestType(
                    id=req.id,
                    person_image_url=req.person_image_url,
                    dress_id=req.dress_id,
                    status=TryOnStatusGQL(req.status.value),
                    result_image_url=req.result_image_url,
                    error_message=req.error_message,
                    created_at=req.created_at,
                    completed_at=req.completed_at,
                )
                for req in requests
            ]


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def authenticate_with_apple(self, input: AppleAuthInput) -> AuthResult:
        """
        Authenticate a user with Apple Sign In credentials.
        Creates a new user if they don't exist, or returns existing user.
        """
        # Verify the Apple identity token (skip in development if no token)
        if input.identity_token:
            apple_payload = await verify_apple_identity_token(input.identity_token)
            if not apple_payload and settings.app_env != "development":
                raise Exception("Invalid Apple identity token")
        elif settings.app_env != "development":
            raise Exception("Identity token is required")

        async with async_session_maker() as session:
            # Check if user already exists
            result = await session.execute(
                select(User).where(User.apple_user_id == input.user_identifier)
            )
            user = result.scalar_one_or_none()

            if user:
                # Update last login
                user.last_login_at = datetime.now(timezone.utc)

                # Update user info if provided (Apple only sends this on first sign in)
                if input.email and not user.email:
                    user.email = input.email
                if input.given_name and not user.given_name:
                    user.given_name = input.given_name
                    # Update display name
                    full_name = f"{input.given_name or ''} {input.family_name or ''}".strip()
                    if full_name:
                        user.name = full_name
                if input.family_name and not user.family_name:
                    user.family_name = input.family_name

                await session.commit()
                await session.refresh(user)
            else:
                # Create new user
                full_name = f"{input.given_name or ''} {input.family_name or ''}".strip()
                user = User(
                    id=str(uuid4()),
                    apple_user_id=input.user_identifier,
                    email=input.email,
                    name=full_name if full_name else None,
                    given_name=input.given_name,
                    family_name=input.family_name,
                    last_login_at=datetime.now(timezone.utc),
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)

            # Generate tokens
            access_token = create_access_token(user.id)
            refresh_token = create_refresh_token(user.id)

            return AuthResult(
                user=UserType(
                    id=user.id,
                    email=user.email,
                    name=user.name,
                    apple_user_id=user.apple_user_id,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                ),
                token=access_token,
                refresh_token=refresh_token,
            )

    @strawberry.mutation
    async def refresh_auth_token(self, input: RefreshTokenInput) -> AuthResult:
        """
        Refresh an access token using a refresh token.
        """
        payload = verify_token(input.refresh_token, "refresh")
        if not payload:
            raise Exception("Invalid or expired refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise Exception("Invalid refresh token payload")

        async with async_session_maker() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                raise Exception("User not found")

            if not user.is_active:
                raise Exception("User account is disabled")

            # Generate new tokens
            access_token = create_access_token(user.id)
            new_refresh_token = create_refresh_token(user.id)

            return AuthResult(
                user=UserType(
                    id=user.id,
                    email=user.email,
                    name=user.name,
                    apple_user_id=user.apple_user_id,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                ),
                token=access_token,
                refresh_token=new_refresh_token,
            )

    @strawberry.mutation
    async def create_try_on(self, input: CreateTryOnInput) -> CreateTryOnResult:
        request_id = str(uuid4())
        workflow_id = f"try-on-{request_id}"

        async with async_session_maker() as session:
            # Create the request record
            try_on_request = TryOnRequest(
                id=request_id,
                person_image_url="",  # Will be set after upload
                dress_id=input.dress_id,
                status=TryOnStatus.PENDING,
                temporal_workflow_id=workflow_id,
                user_id=input.user_id,
            )
            session.add(try_on_request)
            await session.commit()

        # Start Temporal workflow with typed input
        client = await get_temporal_client()
        workflow_input = TryOnWorkflowInput(
            request_id=request_id,
            person_image_base64=input.person_image_base64,
            dress_id=input.dress_id,
        )
        await client.start_workflow(
            TryOnWorkflow.run,
            workflow_input,
            id=workflow_id,
            task_queue=settings.temporal_task_queue,
        )

        return CreateTryOnResult(
            id=request_id,
            status=TryOnStatusGQL.PENDING,
            message="Try-on request queued successfully",
        )


schema = strawberry.Schema(query=Query, mutation=Mutation)
