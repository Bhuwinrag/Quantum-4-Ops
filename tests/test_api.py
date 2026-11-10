"""
QUANTUM//OPS - API Endpoints Automated Test Suite
Tests FastAPI routes, CORS, schemas, and system information contracts.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check():
    """Verify /api/health returns 200 and healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "QUANTUM//OPS"
    assert "version" in data


def test_system_info():
    """Verify /api/system/info returns valid hardware telemetry."""
    response = client.get("/api/system/info")
    assert response.status_code == 200
    data = response.json()
    assert data["system_name"] == "QUANTUM//OPS"
    assert "os" in data
    assert "cpu" in data
    assert "cpu_cores" in data
    assert data["cpu_cores"] > 0
    assert "ram_gb" in data
    assert data["ram_gb"] > 0
    assert "active_execution_mode" in data
    assert data["active_execution_mode"] in ("cpu_simulator", "gpu_simulator")
    assert "modules" in data


def test_list_modules():
    """Verify /api/modules lists all 4 quantum modules."""
    response = client.get("/api/modules")
    assert response.status_code == 200
    data = response.json()
    assert "cudaq" in data
    assert "qiskit" in data
    assert "nvqlink" in data
    assert "shor" in data

    # Verify status contract fields
    for mod_key in ("cudaq", "qiskit", "nvqlink", "shor"):
        mod = data[mod_key]
        assert "module" in mod
        assert "status" in mod
        assert mod["status"] in ("success", "simulated", "unavailable", "error", "initializing")
        assert "execution_mode" in mod


def test_get_individual_module_status():
    """Verify /api/modules/{module_name}/status endpoint."""
    for mod_key in ("cudaq", "qiskit", "nvqlink", "shor"):
        response = client.get(f"/api/modules/{mod_key}/status")
        assert response.status_code == 200
        data = response.json()
        assert data["module"]
        assert "status" in data


def test_get_nonexistent_module_status():
    """Verify non-existent module returns 404."""
    response = client.get("/api/modules/unknown_quantum_device/status")
    assert response.status_code == 404


def test_execute_endpoint_valid_command():
    """Verify /api/execute runs commands properly."""
    payload = {"command": "help", "raw_input": "help"}
    response = client.post("/api/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "QUANTUM//OPS WORKBENCH COMMAND MANUAL" in data["output"]
