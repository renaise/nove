import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.worker.workflow_sandbox import (
    SandboxedWorkflowRunner,
    SandboxRestrictions,
)

from src.core.config import settings
from src.temporal.activities import try_on_activities
from src.temporal.workflows import TryOnWorkflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_worker():
    """Run the Temporal worker with proper sandbox configuration."""
    logger.info(f"Connecting to Temporal at {settings.temporal_host}")

    client = await Client.connect(
        settings.temporal_host,
        namespace=settings.temporal_namespace,
    )

    # Configure sandbox restrictions to pass through modules that are safe
    # This prevents the sandbox from trying to reload these modules
    restrictions = SandboxRestrictions.default.with_passthrough_modules(
        # Standard library modules
        "dataclasses",
        "datetime",
        "logging",
        # Pass through our modules that the workflow needs
        "src",
        "src.temporal",
        "src.temporal.activities",
        "src.temporal.workflows",
        "src.models",
        "src.core",
        "src.services",
    )

    workflow_runner = SandboxedWorkflowRunner(restrictions=restrictions)

    worker = Worker(
        client,
        task_queue=settings.temporal_task_queue,
        workflows=[TryOnWorkflow],
        activities=try_on_activities,
        workflow_runner=workflow_runner,
    )

    logger.info(f"Starting worker on task queue: {settings.temporal_task_queue}")
    await worker.run()


def main():
    """Entry point for the worker."""
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
