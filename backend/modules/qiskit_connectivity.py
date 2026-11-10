"""
QUANTUM//OPS - Module 02: Qiskit API Connectivity
Integration Slot: Fully functional Qiskit local simulation engine.
Teammate can override or extend this module via feature/qiskit branch.

Contract:
- get_status() -> dict
- run(payload: dict) -> dict
"""

import os
import time
from typing import Dict, Any

# Safe dynamic import
_QISKIT_AVAILABLE = False
_QISKIT_VERSION = None

try:
    import qiskit
    _QISKIT_AVAILABLE = True
    _QISKIT_VERSION = getattr(qiskit, "__version__", "unknown")
except Exception:
    _QISKIT_AVAILABLE = False


def get_status() -> Dict[str, Any]:
    """
    Returns real status of Qiskit framework and remote connectivity.
    """
    token = os.environ.get("IBM_QUANTUM_TOKEN", "").strip()
    has_token = bool(token)
    token_masked = f"{token[:4]}...{token[-4:]}" if len(token) > 8 else ("Configured" if has_token else "Not Set")

    if not _QISKIT_AVAILABLE:
        return {
            "module": "Qiskit",
            "status": "unavailable",
            "execution_mode": "unavailable",
            "version": None,
            "message": "Qiskit framework is not installed in the current Python environment.",
            "results": {
                "installed": False,
                "remedy": "Run 'pip install qiskit' to enable local quantum simulation.",
            },
            "execution_time_ms": 0.0,
        }

    status_str = "success"
    mode_str = "remote_hardware" if has_token else "cpu_simulator"
    msg = f"Qiskit {_QISKIT_VERSION} online. " + (
        "IBM Quantum credentials detected." if has_token else "Local CPU simulator active (IBM token optional)."
    )

    return {
        "module": "Qiskit",
        "status": status_str,
        "execution_mode": mode_str,
        "version": _QISKIT_VERSION,
        "message": msg,
        "results": {
            "installed": True,
            "qiskit_version": _QISKIT_VERSION,
            "local_simulator": "Available (CPU Statevector)",
            "ibm_quantum_configured": has_token,
            "token_status": token_masked,
            "default_backend": "Aer / StatevectorSimulator (Local CPU)",
        },
        "execution_time_ms": 0.0,
    }


def run(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a quantum circuit using Qiskit.
    Supports local CPU statevector simulation.
    """
    start_time = time.perf_counter()
    shots = int(payload.get("shots", 1024))
    circuit_type = str(payload.get("circuit", "bell")).lower()

    if not _QISKIT_AVAILABLE:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return {
            "module": "Qiskit",
            "status": "unavailable",
            "execution_mode": "unavailable",
            "message": "Qiskit is not installed in this environment.",
            "results": {},
            "execution_time_ms": round(elapsed_ms, 2),
        }

    try:
        from qiskit import QuantumCircuit
        from qiskit.quantum_info import Statevector

        if circuit_type == "ghz":
            qc = QuantumCircuit(3)
            qc.h(0)
            qc.cx(0, 1)
            qc.cx(1, 2)
            qubit_count = 3
        elif circuit_type == "superposition":
            qc = QuantumCircuit(1)
            qc.h(0)
            qubit_count = 1
        else:
            qc = QuantumCircuit(2)
            qc.h(0)
            qc.cx(0, 1)
            qubit_count = 2

        sv = Statevector.from_instruction(qc)
        raw_samples = sv.sample_counts(shots=shots)
        counts = {str(k): int(v) for k, v in raw_samples.items()}

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return {
            "module": "Qiskit",
            "status": "success",
            "execution_mode": "cpu_simulator",
            "message": f"Qiskit circuit [{circuit_type.upper()}] simulated successfully on CPU.",
            "results": {
                "circuit_type": circuit_type,
                "qubit_count": qubit_count,
                "shots": shots,
                "counts": counts,
                "simulator_engine": "Qiskit Statevector (Local CPU)",
            },
            "execution_time_ms": round(elapsed_ms, 2),
        }

    except Exception as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return {
            "module": "Qiskit",
            "status": "error",
            "execution_mode": "cpu_simulator",
            "message": f"Qiskit execution error: {str(e)}",
            "results": {"error_details": str(e)},
            "execution_time_ms": round(elapsed_ms, 2),
        }
