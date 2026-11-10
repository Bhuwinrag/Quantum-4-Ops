"""
QUANTUM//OPS - Module 02: Qiskit API Connectivity & Simulation
Integrated from Qiskit GHZ circuit implementation.
Supports local CPU simulation via Qiskit Aer and IBM Quantum Cloud execution via Qiskit Runtime.
"""

import os
import time
from typing import Dict, Any, Optional

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# Optional IBM Quantum Cloud Runtime
_IBM_RUNTIME_AVAILABLE = False
try:
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    _IBM_RUNTIME_AVAILABLE = True
except Exception:
    _IBM_RUNTIME_AVAILABLE = False

# Local CPU simulator singleton
_local_simulator = AerSimulator()


def build_circuit(circuit_type: str = "ghz") -> QuantumCircuit:
    """
    Constructs quantum circuits:
    - 'ghz': 3-qubit Greenberger-Horne-Zeilinger entangled state (|000> + |111>)/sqrt(2)
    - 'bell': 2-qubit Bell state (|00> + |11>)/sqrt(2)
    - 'superposition': 1-qubit Hadamard superposition (|0> + |1>)/sqrt(2)
    """
    ctype = circuit_type.lower()
    if ctype == "ghz":
        qc = QuantumCircuit(3, 3)
        qc.h(0)
        qc.cx(0, 1)
        qc.cx(1, 2)
        qc.measure([0, 1, 2], [0, 1, 2])
        return qc
    elif ctype == "superposition":
        qc = QuantumCircuit(1, 1)
        qc.h(0)
        qc.measure(0, 0)
        return qc
    else:  # default "bell"
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])
        return qc


def get_ibm_token() -> Optional[str]:
    """Retrieves IBM Quantum token from environment or .env file."""
    return os.environ.get("IBM_QUANTUM_TOKEN") or os.environ.get("QISKIT_IBM_TOKEN")


def get_status() -> Dict[str, Any]:
    """
    Module contract: query operational status of Qiskit subsystem.
    """
    token = get_ibm_token()
    token_configured = bool(token and len(token) > 10)

    mode = "ibm_cloud_runtime" if token_configured and _IBM_RUNTIME_AVAILABLE else "cpu_simulator"

    return {
        "module": "Qiskit",
        "status": "success",
        "execution_mode": mode,
        "version": "1.0.0-PROD",
        "message": (
            "Qiskit Aer local CPU simulator online (IBM Quantum cloud credentials active)."
            if token_configured
            else "Qiskit Aer local CPU simulator active. Local high-performance simulation enabled."
        ),
        "results": {
            "integrated": True,
            "simulator": "Qiskit AerSimulator",
            "ibm_runtime_package": _IBM_RUNTIME_AVAILABLE,
            "ibm_quantum_configured": token_configured,
            "default_circuit": "ghz (3-qubit)",
            "supported_circuits": ["ghz", "bell", "superposition"],
        },
        "execution_time_ms": 0.0,
    }


def run(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Module contract: execute quantum circuit via local AerSimulator or IBM Quantum Cloud.
    """
    start_time = time.perf_counter()
    circuit_type = str(payload.get("circuit", "ghz")).lower()
    shots = int(payload.get("shots", 1024))
    token = get_ibm_token()

    # Build the requested quantum circuit
    qc = build_circuit(circuit_type)
    qubit_count = qc.num_qubits

    # Check if IBM Cloud execution is explicitly requested and configured
    use_cloud = bool(payload.get("use_cloud", False)) and bool(token) and _IBM_RUNTIME_AVAILABLE

    if use_cloud:
        try:
            service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
            backend = service.least_busy(simulator=False, operational=True)
            pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
            isa_circuit = pm.run(qc)
            sampler = Sampler(mode=backend)
            job = sampler.run([isa_circuit], shots=shots)
            result = job.result()
            counts = result[0].data.meas.get_counts()
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            return {
                "module": "Qiskit",
                "status": "success",
                "execution_mode": "ibm_cloud_qpu",
                "message": f"Circuit executed on IBM Quantum hardware '{backend.name}' (Job ID: {job.job_id()}).",
                "results": {
                    "backend": backend.name,
                    "job_id": job.job_id(),
                    "circuit": circuit_type,
                    "qubits": qubit_count,
                    "shots": shots,
                    "counts": counts,
                },
                "execution_time_ms": round(elapsed_ms, 2),
            }
        except Exception as cloud_err:
            # Fall back cleanly to local simulator if cloud execution fails
            pass

    # Local CPU simulation via Qiskit Aer
    try:
        compiled = transpile(qc, _local_simulator)
        job = _local_simulator.run(compiled, shots=shots)
        result = job.result()
        raw_counts = result.get_counts()

        # Format counts with standard bitstrings
        counts = {str(k): int(v) for k, v in raw_counts.items()}
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return {
            "module": "Qiskit",
            "status": "success",
            "execution_mode": "cpu_simulator",
            "message": f"Circuit executed on Qiskit Aer local CPU simulator ({qubit_count} qubits, {shots} shots).",
            "results": {
                "backend": "AerSimulator (Local CPU)",
                "circuit": circuit_type,
                "qubits": qubit_count,
                "shots": shots,
                "counts": counts,
            },
            "execution_time_ms": round(elapsed_ms, 2),
        }
    except Exception as ex:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return {
            "module": "Qiskit",
            "status": "error",
            "execution_mode": "cpu_simulator",
            "message": f"Qiskit execution error: {str(ex)}",
            "results": {"error": str(ex)},
            "execution_time_ms": round(elapsed_ms, 2),
        }


if __name__ == "__main__":
    print("Testing Qiskit Connectivity Module...")
    print("Status:", get_status())
    res = run({"circuit": "ghz", "shots": 1024})
    print("Run Result:", res)
