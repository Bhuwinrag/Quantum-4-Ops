"""
QUANTUM//OPS - Asynchronous Execution Manager
Dispatches long-running quantum simulations to a worker thread pool
to ensure the FastAPI async event loop is never blocked.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any
from backend.module_registry import registry
from backend.schemas import ModuleExecutionResponse
from backend.utils.logger import logger


class ExecutionManager:
    """Manages thread-isolated quantum execution."""

    def __init__(self, max_workers: int = 4):
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="quantum_worker")

    async def execute_module_async(
        self, module_key: str, payload: Dict[str, Any]
    ) -> ModuleExecutionResponse:
        """
        Executes module in thread pool to prevent blocking the async event loop.
        """
        loop = asyncio.get_running_loop()
        try:
            response = await loop.run_in_executor(
                self._executor, registry.execute, module_key, payload
            )
            return response
        except Exception as e:
            logger.error(f"Execution manager caught fatal thread error: {e}")
            return ModuleExecutionResponse(
                module=module_key.upper(),
                status="error",
                execution_mode="unavailable",
                message=f"Simulation thread execution failed: {str(e)}",
                results={"error": str(e)},
                execution_time_ms=0.0,
            )

    def shutdown(self):
        """Cleanly releases worker threads."""
        self._executor.shutdown(wait=False)


# Global execution manager singleton
execution_manager = ExecutionManager()
