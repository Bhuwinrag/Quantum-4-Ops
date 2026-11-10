# -*- coding: utf-8 -*-
"""
QUANTUM//OPS - Module 02: Qiskit Connectivity Test Adapter
Direct bridge and test harness for Qiskit integration.
"""

import os
from backend.modules.qiskit_connectivity import get_status, run, build_circuit

# Compatibility aliases
def execute_ghz(shots: int = 1024):
    return run({"circuit": "ghz", "shots": shots})

if __name__ == "__main__":
    print("\n--- QISKIT GHZ CIRCUIT TEST ---")
    st = get_status()
    print("Status:", st["message"])
    res = run({"circuit": "ghz", "shots": 1024})
    print("Execution Mode:", res["execution_mode"])
    print("Measurement Counts:", res["results"]["counts"])
