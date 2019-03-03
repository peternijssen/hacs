"""Helper functions for HACS."""
import asyncio


async def run_tasks(tasks):
    """Run tasks in background."""
    for task in asyncio.as_completed(tasks):
        await task
