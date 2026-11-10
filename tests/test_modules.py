"""
QUANTUM//OPS - Quantum Engine Modules Test Suite
Tests module registry discovery, integrated modules (CUDA-Q, Qiskit, Shor),
and graceful fallback for unpushed modules (NVQLink).
"""

import pytest
from backend.module_registry import registry
from backend.modules import cudaq_engine, qiskit_connectivity, shors_algorithm


def test_registry_discovery():
    """Verify registry discovers all 4 quantum module slots."""
    for key in ("cudaq", "qiskit", "nvqlink", "shor"):
        mod = registry.get(key)
        assert mod is not None, f"Module slot '{key}' not found in registry"
        st = mod.query_status()
        assert st.module
        assert st.status in ("success", "simulated", "unavailable", "error")
        assert hasattr(st, "results")
        assert isinstance(st.results, dict)


def test_cudaq_contract_and_execution():
    """Verify CUDA-Q module complies with contract."""
    status = cudaq_engine.get_status()
    assert isinstance(status, dict)
    assert status["module"] == "CUDA-Q"
    assert status["status"] in ("success", "simulated", "unavailable")
    assert "execution_mode" in status
    assert "results" in status

    # Run execution test
    exec_res = cudaq_engine.run({"circuit": "bell", "shots": 100})
    assert isinstance(exec_res, dict)
    assert exec_res["status"] in ("success", "simulated", "unavailable")
    if exec_res["status"] in ("success", "simulated"):
        assert "counts" in exec_res["results"]


def test_qiskit_contract_and_execution():
    """Verify Qiskit module status and local Aer circuit execution."""
    status = qiskit_connectivity.get_status()
    assert isinstance(status, dict)
    assert status["module"] == "Qiskit"
    assert status["status"] == "success"
    assert status["execution_mode"] in ("cpu_simulator", "ibm_cloud_runtime")

    # Run 3-qubit GHZ circuit execution test
    exec_res = qiskit_connectivity.run({"circuit": "ghz", "shots": 200})
    assert isinstance(exec_res, dict)
    assert exec_res["status"] == "success"
    assert "counts" in exec_res["results"]
    assert exec_res["results"]["qubits"] == 3


def test_shors_algorithm_contract_and_execution():
    """Verify Shor's quantum factoring engine status and factorization."""
    status = shors_algorithm.get_status()
    assert isinstance(status, dict)
    assert status["module"] == "Shor"
    assert status["status"] == "success"

    # Factor N = 15
    exec_res = shors_algorithm.run({"number": 15, "base": 7, "shots": 100})
    assert isinstance(exec_res, dict)
    assert exec_res["status"] == "success"
    assert exec_res["results"]["factors"] == [3, 5]
    assert exec_res["results"]["input_number"] == 15


def test_unpushed_nvqlink_graceful_handling():
    """Verify that unpushed NVQLink module reports unavailable cleanly without crashing."""
    mod = registry.get("nvqlink")
    assert mod is not None
    status = mod.query_status()
    assert status.status == "unavailable"
    assert status.execution_mode == "unavailable"
    assert "awaiting" in status.message.lower() or "not found" in status.message.lower()

    # Executing unpushed module returns unavailable cleanly
    res = registry.execute("nvqlink", {"shots": 100})
    assert res.status == "unavailable"
    assert res.execution_mode == "unavailable"
    assert "awaiting" in res.message.lower() or "not been pushed" in res.message.lower()


def test_missing_module_graceful_handling():
    """Ensure querying or executing an unknown module key does not crash the system."""
    res = registry.execute("non_existent_engine", {"test": True})
    assert res.status == "unavailable"
    assert "unknown module" in res.message.lower() or "unavailable" in res.message.lower()
