from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow

# Pass through activity imports - they'll be used by reference
with workflow.unsafe.imports_passed_through():
    from src.temporal.activities import (
        upload_person_image,
        get_dress_image_url,
        generate_try_on_image,
        update_request_result,
    )


@dataclass
class TryOnWorkflowInput:
    """Type-safe input for try-on workflow."""

    request_id: str
    person_image_base64: str
    dress_id: str


@dataclass
class TryOnWorkflowOutput:
    """Type-safe output from try-on workflow."""

    success: bool
    result_url: str | None = None
    error: str | None = None


@workflow.defn
class TryOnWorkflow:
    """Workflow for processing virtual try-on requests."""

    @workflow.run
    async def run(self, input_data: TryOnWorkflowInput) -> TryOnWorkflowOutput:
        """
        Execute the try-on workflow.

        Steps:
        1. Upload person image to storage
        2. Get dress image URL from database
        3. Generate try-on image using Nano Banana Pro
        4. Update request with result
        """
        try:
            # Step 1: Upload person image
            person_image_url: str = await workflow.execute_activity(
                upload_person_image,
                input_data,
                start_to_close_timeout=timedelta(seconds=60),
            )

            # Step 2: Get dress image URL
            dress_image_url: str = await workflow.execute_activity(
                get_dress_image_url,
                input_data.dress_id,
                start_to_close_timeout=timedelta(seconds=10),
            )

            # Step 3: Generate try-on image (this can take a while)
            try_on_result: dict = await workflow.execute_activity(
                generate_try_on_image,
                (input_data.request_id, person_image_url, dress_image_url),
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=workflow.RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=5),
                    backoff_coefficient=2.0,
                ),
            )

            # Step 4: Update request with result
            await workflow.execute_activity(
                update_request_result,
                (input_data.request_id, try_on_result),
                start_to_close_timeout=timedelta(seconds=30),
            )

            return TryOnWorkflowOutput(
                success=try_on_result["success"],
                result_url=try_on_result.get("result_url"),
                error=try_on_result.get("error"),
            )

        except Exception as e:
            return TryOnWorkflowOutput(
                success=False,
                error=f"Workflow failed: {str(e)}",
            )
