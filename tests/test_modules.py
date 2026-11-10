"""
QUANTUM//OPS - Quantum Engine Modules Test Suite
Tests module registry discovery, missing module file handling, and CUDA-Q execution.
"""

import pytest
from backend.module_registry import registry
from backend.modules import cudaq_engine


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
    assert status["status"] in ("success", "unavailable")
    assert "execution_mode" in status
    assert "results" in status

    # Run execution test
    exec_res = cudaq_engine.run({"circuit": "bell", "shots": 100})
    assert isinstance(exec_res, dict)
    assert exec_res["status"] in ("success", "unavailable")


def test_unpushed_modules_graceful_status():
    """Verify that unpushed teammate modules report unavailable cleanly without crashing."""
    for key in ("qiskit", "nvqlink", "shor"):
        mod = registry.get(key)
        assert mod is not None
        status = mod.query_status()
        assert status.status == "unavailable"
        assert status.execution_mode == "unavailable"
        assert "awaiting" in status.message.lower() or "not found" in status.message.lower()


def test_unpushed_modules_graceful_execution():
    """Verify executing an unpushed teammate module returns clean failure without 500 error."""
    for key in ("qiskit", "nvqlink", "shor"):
        res = registry.execute(key, {"shots": 100})
        assert res.status == "unavailable"
        assert res.execution_mode == "unavailable"
        assert "awaiting" in res.message.lower() or "not been pushed" in res.message.lower()


def test_missing_module_graceful_handling():
    """Ensure querying or executing an unknown module key does not crash the system."""
    res = registry.execute("non_existent_engine", {"test": True})
    assert res.status == "unavailable"
    assert "unknown module" in res.message.lower() or "unavailable" in res.message.lower()
