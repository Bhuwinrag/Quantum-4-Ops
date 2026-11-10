"""
QUANTUM//OPS - Centralized Module Registry
Dynamic module loader, dependency isolator, and contract validator.
Guarantees the application starts and runs even if modules or dependencies are missing.
"""

import os
import sys
import importlib
import traceback
from typing import Dict, Any, Optional, Callable
from backend.schemas import ModuleStatusResponse, ModuleExecutionResponse
from backend.utils.logger import logger

# Module definitions and metadata
MODULE_MANIFEST = {
    "cudaq": {
        "id": "cudaq",
        "display_name": "01 CUDA-Q ENGINE",
        "role": "CUDA-Q Hybrid Kernel Simulation",
        "module_path": "backend.modules.cudaq_engine",
        "file_name": "cudaq_engine.py",
        "description": "NVIDIA CUDA-Q hybrid quantum-classical simulation platform",
    },
    "qiskit": {
        "id": "qiskit",
        "display_name": "02 QISKIT CONNECTIVITY",
        "role": "Qiskit Statevector & IBM API",
        "module_path": "backend.modules.qiskit_connectivity",
        "file_name": "qiskit_connectivity.py",
        "description": "Qiskit local statevector simulator and IBM Quantum cloud connectivity",
    },
    "nvqlink": {
        "id": "nvqlink",
        "display_name": "03 NVQLINK ARCHITECTURE",
        "role": "Coherent GPU-QPU Memory Fabric",
        "module_path": "backend.modules.nvqlink_demo",
        "file_name": "nvqlink_demo.py",
        "description": "NVIDIA NVQLink coherent GPU-QPU memory fabric architecture simulation",
    },
    "shor": {
        "id": "shor",
        "display_name": "04 SHOR'S ALGORITHM",
        "role": "Quantum Factoring Engine (N=15)",
        "module_path": "backend.modules.shors_algorithm",
        "file_name": "shors_algorithm.py",
        "description": "Shor's quantum order-finding factorization demonstration (N = 15)",
    },
}


class RegisteredModule:
    """Represents a dynamically loaded module or an isolated fallback placeholder."""

    def __init__(self, key: str, meta: Dict[str, Any]):
        self.key = key
        self.meta = meta
        self.get_status_fn: Optional[Callable[[], dict]] = None
        self.run_fn: Optional[Callable[[dict], dict]] = None
        self.loaded = False
        self.error_detail: Optional[str] = None
        self.cached_status: Optional[ModuleStatusResponse] = None

    def load(self) -> None:
        """Attempts dynamic import and interface validation."""
        module_path = self.meta["module_path"]
        try:
            # Check if file physically exists
            module_dir = os.path.dirname(__file__)
            target_file = os.path.join(module_dir, "modules", self.meta["file_name"])
            if not os.path.isfile(target_file):
                self.loaded = False
                self.error_detail = f"Module file not found: {self.meta['file_name']} (awaiting teammate push)"
                logger.info(f"[{self.key.upper()}] Integration slot ready: awaiting {self.meta['file_name']}")
                return

            # Import or reload
            if module_path in sys.modules:
                mod = importlib.reload(sys.modules[module_path])
            else:
                mod = importlib.import_module(module_path)

            # Contract verification
            get_status_fn = getattr(mod, "get_status", None)
            run_fn = getattr(mod, "run", None)

            if not callable(get_status_fn) or not callable(run_fn):
                self.loaded = False
                self.error_detail = "Module violates interface contract: missing get_status() or run()."
                logger.warning(f"[{self.key.upper()}] {self.error_detail}")
                return

            self.get_status_fn = get_status_fn
            self.run_fn = run_fn
            self.loaded = True
            self.error_detail = None
            logger.info(f"[{self.key.upper()}] Module loaded: {self.meta['display_name']}")

        except Exception as e:
            self.loaded = False
            self.error_detail = f"Import error: {str(e)}"
            logger.warning(f"[{self.key.upper()}] Failed to load: {self.error_detail}")

    def query_status(self) -> ModuleStatusResponse:
        """Invokes get_status() safely and validates output."""
        if not self.loaded or not self.get_status_fn:
            return ModuleStatusResponse(
                module=self.meta["display_name"],
                status="unavailable",
                execution_mode="unavailable",
                version=None,
                description=self.meta["description"],
                hardware_target=None,
                message=self.error_detail or f"Integration slot ready: awaiting {self.meta['file_name']} from teammate push.",
                results={
                    "file": self.meta["file_name"],
                    "status": "Awaiting teammate push",
                    "integrated": False,
                },
                details={"file": self.meta["file_name"]},
            )

        try:
            raw = self.get_status_fn()
            raw["module"] = self.meta["display_name"]
            raw["description"] = self.meta["description"]

            if "results" not in raw and "details" in raw:
                raw["results"] = raw["details"]
            elif "details" not in raw and "results" in raw:
                raw["details"] = raw["results"]

            status_obj = ModuleStatusResponse(**raw)
            self.cached_status = status_obj
            return status_obj
        except Exception as ex:
            logger.error(f"[{self.key}] get_status() raised exception: {ex}")
            return ModuleStatusResponse(
                module=self.meta["display_name"],
                status="error",
                execution_mode="unavailable",
                version=None,
                description=self.meta["description"],
                message=f"Status check exception: {str(ex)}",
                results={"error": str(ex)},
                details={"traceback": traceback.format_exc()},
            )

    def execute(self, payload: Dict[str, Any]) -> ModuleExecutionResponse:
        """Invokes run() safely and validates output against contract."""
        if not self.loaded or not self.run_fn:
            return ModuleExecutionResponse(
                module=self.meta["display_name"],
                status="unavailable",
                execution_mode="unavailable",
                message=(
                    f"Execution halted: {self.meta['display_name']} ({self.meta['file_name']}) has not been pushed yet. "
                    f"Awaiting teammate contribution."
                ),
                results={"file": self.meta["file_name"], "integrated": False},
                execution_time_ms=0.0,
            )

        try:
            raw = self.run_fn(payload)
            raw["module"] = self.meta["display_name"]
            if "status" not in raw:
                raw["status"] = "success"
            if "execution_mode" not in raw:
                raw["execution_mode"] = "cpu_simulator"
            if "message" not in raw:
                raw["message"] = "Execution finished."
            if "results" not in raw:
                raw["results"] = {}
            if "details" not in raw:
                raw["details"] = raw["results"]
            if "execution_time_ms" not in raw:
                raw["execution_time_ms"] = 0.0

            return ModuleExecutionResponse(**raw)
        except Exception as ex:
            logger.error(f"[{self.key}] run() raised exception: {ex}")
            return ModuleExecutionResponse(
                module=self.meta["display_name"],
                status="error",
                execution_mode="unavailable",
                message=f"Execution error: {str(ex)}",
                results={"error_details": str(ex), "traceback": traceback.format_exc()},
                execution_time_ms=0.0,
            )


class ModuleRegistry:
    """Central registry manager singleton."""

    def __init__(self):
        self._modules: Dict[str, RegisteredModule] = {}
        self.initialize()

    def initialize(self) -> None:
        """Initializes and registers all manifest entries."""
        for key, meta in MODULE_MANIFEST.items():
            reg_mod = RegisteredModule(key, meta)
            reg_mod.load()
            self._modules[key] = reg_mod

    def get(self, key: str) -> Optional[RegisteredModule]:
        return self._modules.get(key.lower())

    def get_all_statuses(self) -> Dict[str, ModuleStatusResponse]:
        """Queries and returns statuses for all registered modules."""
        return {key: mod.query_status() for key, mod in self._modules.items()}

    def get_status_summary(self) -> Dict[str, str]:
        """Returns brief status strings per module (e.g. {'cudaq': 'unavailable'})."""
        return {key: mod.query_status().status for key, mod in self._modules.items()}

    def execute(self, module_key: str, payload: Dict[str, Any]) -> ModuleExecutionResponse:
        """Executes the specified module safely."""
        mod = self.get(module_key)
        if not mod:
            return ModuleExecutionResponse(
                module=module_key.upper(),
                status="unavailable",
                execution_mode="unavailable",
                message=f"Unknown module '{module_key}'. Available: {list(self._modules.keys())}",
                results={},
                execution_time_ms=0.0,
            )
        return mod.execute(payload)


# Global registry singleton
registry = ModuleRegistry()
