"""
QUANTUM//OPS - Pydantic Schemas and Contracts
Strict typing and response validation for API and Module registry.
"""

from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, Field

# Contract Enums
StatusType = Literal["success", "error", "simulated", "unavailable", "initializing"]
ExecutionModeType = Literal[
    "cpu_simulator",
    "gpu_simulator",
    "remote_hardware",
    "architecture_simulation",
    "unavailable",
]


class ModuleStatusResponse(BaseModel):
    """Status contract returned by every module's get_status()."""
    module: str
    status: StatusType
    execution_mode: ExecutionModeType
    version: Optional[str] = None
    description: Optional[str] = None
    hardware_target: Optional[str] = None
    message: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class ModuleExecutionResponse(BaseModel):
    """Execution contract returned by every module's run(payload)."""
    module: str
    status: StatusType
    execution_mode: ExecutionModeType
    message: str
    results: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float = 0.0
    command: Optional[str] = None
    error: Optional[str] = None


class CommandRequest(BaseModel):
    """Payload sent from terminal interface to /api/execute."""
    command: str
    args: List[str] = Field(default_factory=list)
    raw_input: Optional[str] = None


class CommandResponse(BaseModel):
    """Structured response returned by /api/execute."""
    status: Literal["success", "error", "simulated", "unavailable"]
    command: str
    output: str
    data: Optional[Dict[str, Any]] = None
    execution_time_ms: float = 0.0


class SystemInfoResponse(BaseModel):
    """Response returned by /api/system/info."""
    system_name: str = "QUANTUM//OPS"
    full_name: str = "Quantum Hybrid Computing Workbench"
    tagline: str = "BREAK THE BOUNDARIES OF COMPUTING."
    version: str = "1.0.0-PROD"
    os: str
    os_release: str
    architecture: str
    python_version: str
    cpu: str
    cpu_cores: int
    ram_gb: float
    gpu_detected: bool
    gpu_name: Optional[str] = None
    cuda_available: bool
    active_execution_mode: str
    modules: Dict[str, str] = Field(default_factory=dict)
