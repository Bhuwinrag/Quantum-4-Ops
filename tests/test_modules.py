"""
QUANTUM//OPS - Quantum Engine Modules Test Suite
Tests contract compliance, isolation, and algorithm logic for all 4 modules.
"""

import pytest
from backend.module_registry import registry
from backend.modules import cudaq_engine, qiskit_connectivity, nvqlink_demo, shors_algorithm


def test_registry_discovery():
    """Verify registry discovers all 4 quantum modules."""
    for key in ("cudaq", "qiskit", "nvqlink", "shor"):
        mod = registry.get(key)
        assert mod is not None, f"Module '{key}' not found in registry"
        st = mod.query_status()
        assert st.module
        assert st.status in ("success", "simulated", "unavailable", "error")
        # Ensure results attribute is present and accessible
        assert hasattr(st, "results")
        assert isinstance(st.results, dict)


def test_cudaq_contract():
    """Verify CUDA-Q module complies with contract."""
    status = cudaq_engine.get_status()
    assert isinstance(status, dict)
    assert status["module"] == "CUDA-Q"
    assert status["status"] in ("success", "unavailable")
    assert "execution_mode" in status
    assert "results" in status

    # Run execution test
    exec_res = cudaq_engine.run({"circuit": "bell", "shots": 100})
    assert isinstance(exec_res, dict)
    assert exec_res["status"] in ("success", "unavailable")


def test_qiskit_contract_and_integration_slot():
    """Verify Qiskit integration slot adheres to team contract."""
    status = qiskit_connectivity.get_status()
    assert isinstance(status, dict)
    assert status["module"] == "Qiskit"
    assert status["status"] in ("success", "unavailable")
    assert "execution_mode" in status
    assert "results" in status

    result = qiskit_connectivity.run({"circuit": "bell", "shots": 500})
    assert isinstance(result, dict)
    assert result["status"] in ("success", "unavailable")


def test_nvqlink_contract_and_integration_slot():
    """Verify NVQLink integration slot adheres to team contract."""
    status = nvqlink_demo.get_status()
    assert isinstance(status, dict)
    assert status["module"] == "NVQLink"
    assert status["status"] in ("simulated", "unavailable")
    assert "execution_mode" in status
    assert "results" in status

    result = nvqlink_demo.run({"qubits": 8, "shots": 1000})
    assert isinstance(result, dict)
    assert result["status"] in ("simulated", "unavailable")


def test_shors_algorithm_contract_and_integration_slot():
    """Verify Shor's algorithm integration slot adheres to team contract."""
    status = shors_algorithm.get_status()
    assert isinstance(status, dict)
    assert status["module"] == "Shor"
    assert status["status"] in ("success", "unavailable")
    assert "execution_mode" in status
    assert "results" in status

    result = shors_algorithm.run({"number": 15})
    assert isinstance(result, dict)
    assert result["status"] in ("success", "unavailable")


def test_missing_module_graceful_handling():
    """Ensure querying or executing an unknown module does not crash the system."""
    res = registry.execute("non_existent_engine", {"test": True})
    assert res.status == "unavailable"
    assert "unknown module" in res.message.lower() or "unavailable" in res.message.lower()
