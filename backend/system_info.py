"""
QUANTUM//OPS - System Information Service
Combines hardware diagnostics and module telemetry.
"""

from typing import Dict, Any
from backend.schemas import SystemInfoResponse
from backend.services.hardware_detector import HardwareDetector


def get_full_system_info(module_statuses: Dict[str, str]) -> SystemInfoResponse:
    """Builds the comprehensive SystemInfoResponse model."""
    hw = HardwareDetector.get_system_summary()
    return SystemInfoResponse(
        system_name="QUANTUM//OPS",
        full_name="Quantum Hybrid Computing Workbench",
        tagline="BREAK THE BOUNDARIES OF COMPUTING.",
        version="1.0.0-PROD",
        os=hw["os"],
        os_release=hw["os_release"],
        architecture=hw["architecture"],
        python_version=hw["python_version"],
        cpu=hw["cpu"],
        cpu_cores=hw["cpu_cores"],
        ram_gb=hw["ram_gb"],
        gpu_detected=hw["gpu_detected"],
        gpu_name=hw["gpu_name"],
        cuda_available=hw["cuda_available"],
        active_execution_mode=hw["active_execution_mode"],
        modules=module_statuses,
    )
