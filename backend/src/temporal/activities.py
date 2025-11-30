import logging
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from temporalio import activity

# Activities run OUTSIDE the sandbox, so these imports are safe
from src.core.database import async_session_maker
from src.models.dress import Dress
from src.models.try_on import TryOnRequest, TryOnStatus
from src.services.genai import genai_service
from src.services.storage import storage_service

logger = logging.getLogger(__name__)


@dataclass
class TryOnWorkflowInput:
    """Type-safe input for try-on workflow (duplicated for activity use)."""

    request_id: str
    person_image_base64: str
    dress_id: str


@activity.defn
async def upload_person_image(input_data: TryOnWorkflowInput) -> str:
    """Upload the person image to storage and update the request."""
    logger.info(f"Uploading person image for request {input_data.request_id}")

    result = await storage_service.upload_base64_image(
        input_data.person_image_base64,
        folder="person-images",
    )

    if not result.success:
        raise Exception(f"Failed to upload person image: {result.error}")

    # Update the request with the person image URL
    async with async_session_maker() as session:
        db_result = await session.execute(
            select(TryOnRequest).where(TryOnRequest.id == input_data.request_id)
        )
        request = db_result.scalar_one()
        request.person_image_url = result.url
        request.status = TryOnStatus.PROCESSING
        await session.commit()

    return result.url


@activity.defn
async def get_dress_image_url(dress_id: str) -> str:
    """Get the dress image URL from the database."""
    logger.info(f"Getting dress image URL for {dress_id}")

    async with async_session_maker() as session:
        result = await session.execute(select(Dress).where(Dress.id == dress_id))
        dress = result.scalar_one_or_none()

        if not dress:
            raise Exception(f"Dress not found: {dress_id}")

        return dress.image_url


@activity.defn
async def generate_try_on_image(
    request_id: str,
    person_image_url: str,
    dress_image_url: str,
) -> dict:
    """Generate the try-on image using Nano Banana Pro."""
    logger.info(f"Generating try-on image for request {request_id}")

    try:
        # Generate the try-on image
        result = await genai_service.generate_try_on_with_url(
            person_image_url,
            dress_image_url,
        )

        if not result.success:
            return {"success": False, "result_url": None, "error": result.error}

        # Upload the result image
        upload_result = await storage_service.upload_image(
            result.image_data,
            folder="try-on-results",
        )

        if not upload_result.success:
            return {"success": False, "result_url": None, "error": upload_result.error}

        return {"success": True, "result_url": upload_result.url, "error": None}

    except Exception as e:
        logger.exception("Failed to generate try-on image")
        return {"success": False, "result_url": None, "error": str(e)}


@activity.defn
async def update_request_result(
    request_id: str,
    output: dict,
) -> None:
    """Update the try-on request with the result."""
    logger.info(f"Updating request {request_id} with result")

    async with async_session_maker() as session:
        result = await session.execute(
            select(TryOnRequest).where(TryOnRequest.id == request_id)
        )
        request = result.scalar_one()

        if output["success"]:
            request.status = TryOnStatus.COMPLETED
            request.result_image_url = output["result_url"]
            request.completed_at = datetime.utcnow()
        else:
            request.status = TryOnStatus.FAILED
            request.error_message = output["error"]

        await session.commit()


# Export all activities for the worker
try_on_activities = [
    upload_person_image,
    get_dress_image_url,
    generate_try_on_image,
    update_request_result,
]
