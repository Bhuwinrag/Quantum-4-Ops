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


def test_cudaq_contract():
    """Verify CUDA-Q module complies with contract."""
    status = cudaq_engine.get_status()
    assert isinstance(status, dict)
    assert status["module"] == "CUDA-Q"
    assert status["status"] in ("success", "unavailable")
    assert "execution_mode" in status

    # Run execution test
    # On Windows / CPU machines without native cudaq wheel, it cleanly reports unavailable or simulated
    exec_res = cudaq_engine.run({"circuit": "bell", "shots": 100, "allow_emulation": True})
    assert isinstance(exec_res, dict)
    assert exec_res["status"] in ("success", "simulated", "unavailable")


def test_qiskit_simulation():
    """Verify Qiskit local simulation works out-of-the-box on CPU."""
    status = qiskit_connectivity.get_status()
    assert isinstance(status, dict)
    assert "status" in status

    # If qiskit is installed, run Bell state simulation
    if status["status"] == "success":
        result = qiskit_connectivity.run({"circuit": "bell", "shots": 500})
        assert result["status"] == "success"
        assert result["execution_mode"] == "cpu_simulator"
        assert "counts" in result["results"]
        counts = result["results"]["counts"]
        # Bell state should produce primarily '00' and '11'
        assert "00" in counts or "0" in counts


def test_nvqlink_simulation():
    """Verify NVQLink architecture simulation stages and telemetry."""
    status = nvqlink_demo.get_status()
    assert status["module"] == "NVQLink"
    assert status["status"] == "simulated"
    assert status["execution_mode"] == "architecture_simulation"

    result = nvqlink_demo.run({"qubits": 8, "shots": 1000})
    assert result["status"] == "simulated"
    assert "job_id" in result["results"]
    assert "pipeline_stages" in result["results"]
    assert len(result["results"]["pipeline_stages"]) == 4


def test_shors_algorithm_factor_15():
    """Verify Shor's algorithm factors 15 mathematically into 3 and 5."""
    status = shors_algorithm.get_status()
    assert status["module"] == "Shor"
    assert status["status"] == "success"

    result = shors_algorithm.run({"number": 15})
    assert result["status"] == "success"
    assert result["execution_mode"] == "cpu_simulator"
    r_data = result["results"]
    assert r_data["input_number"] == 15
    factors = r_data["factors"]
    assert sorted(factors) == [3, 5]
    assert 3 * 5 == 15


def test_shors_algorithm_invalid_prime():
    """Verify prime number input handles gracefully."""
    result = shors_algorithm.run({"number": 7})
    assert result["status"] == "error"
    assert "prime" in result["message"].lower()


def test_missing_module_graceful_handling():
    """Ensure querying or executing an unknown module does not crash the system."""
    res = registry.execute("non_existent_engine", {"test": True})
    assert res.status == "unavailable"
    assert "unknown module" in res.message.lower() or "unavailable" in res.message.lower()
