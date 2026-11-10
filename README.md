# QUANTUM//OPS
### QUANTUM HYBRID COMPUTING WORKBENCH

---

![PYTHON](https://img.shields.io/badge/BACKEND-FASTAPI%20%7C%20PYTHON-00FFFF?style=for-the-badge&logo=fastapi&logoColor=black)
![EXECUTION](https://img.shields.io/badge/EXECUTION-CPU%20%7C%20GPU%20OPTIONAL-557A5F?style=for-the-badge)
![LICENSE](https://img.shields.io/badge/LICENSE-MIT-00FF41?style=for-the-badge)

**QUANTUM//OPS** is an interactive, hacker-inspired hybrid quantum-classical computing workbench built with FastAPI and xterm.js. Designed to look and feel like an internal command console of an advanced quantum computing research laboratory, it integrates four core quantum technologies into a unified execution kernel:

1. **NVIDIA CUDA-Q Engine** — Hybrid quantum-classical computing platform.
2. **Qiskit API Connectivity** — Local CPU statevector simulation and IBM Quantum Runtime integration.
3. **NVIDIA NVQLink Architecture** — Coherent low-latency GPU-QPU memory fabric simulation.
4. **Shor's Factoring Algorithm** — Quantum order-finding and composite integer factorization ($N = 15 = 3 \times 5$).

---

## 🚀 Key Architectural Features

- **Hardware Independence (CPU-First):** Runs natively on standard CPU machines (AMD Ryzen / Intel x86_64, 16 GB RAM) without requiring an NVIDIA GPU to launch or simulate quantum circuits.
- **Dynamic Hardware & GPU Detection:** Real-time probing of CPU cores, physical memory, and optional NVIDIA CUDA hardware via `HardwareDetector`.
- **Fault-Tolerant Dynamic Module Registry:** Missing or in-progress teammate modules never crash the backend. Missing dependencies report `UNAVAILABLE` or `SIMULATED` cleanly.
- **Non-Blocking Threadpool Execution:** Long-running quantum simulations run on worker threads via `ExecutionManager`, keeping FastAPI's async event loop fully responsive.
- **Authentic Cyberpunk Terminal UI:** Pure `#050505` black canvas, `#00FF41` neon green glow, `#00FFFF` cyan accents, CRT scanline raster overlay, live telemetry HUD, command history navigation (Up/Down arrows), and Tab autocompletion.

---

## 👥 Team & Module Ownership

| Module Slot | Module Name | Team Lead / Owner | Git Feature Branch | Target File |
| :--- | :--- | :--- | :--- | :--- |
| **01** | **CUDA-Q ENGINE** | **Bhuwin Rag** *(Team Lead)* | `main` / `feature/cudaq` | `backend/modules/cudaq_engine.py` |
| **02** | **QISKIT CONNECTIVITY** | **DSP** | `feature/qiskit` | `backend/modules/qiskit_connectivity.py` |
| **03** | **NVQLINK ARCHITECTURE** | **Yuva Sekhar** | `feature/nvqlink` | `backend/modules/nvqlink_demo.py` |
| **04** | **SHOR'S ALGORITHM** | **Nikihil** | `feature/shor` | `backend/modules/shors_algorithm.py` |

---

## 📜 The Team Integration Contract

Every team module file in `backend/modules/` **MUST** adhere to this common interface. When team members drop in their updated files, **no changes are required** to the frontend, routing, command handler, or module registry.

```python
from typing import Dict, Any

def get_status() -> Dict[str, Any]:
    """
    Returns the real verified status of the module.
    """
    return {
        "module": "CUDA-Q",                                    # Module name
        "status": "success",                                   # success | simulated | unavailable | error
        "execution_mode": "cpu_simulator",                     # cpu_simulator | gpu_simulator | architecture_simulation | remote_hardware
        "version": "1.0.0",
        "message": "NVIDIA CUDA-Q platform online.",
        "results": {},
        "execution_time_ms": 0.0
    }

def run(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a circuit, simulation, or algorithm run.
    """
    return {
        "module": "CUDA-Q",
        "status": "success",
        "execution_mode": "cpu_simulator",
        "message": "Quantum circuit executed successfully.",
        "results": {
            "counts": {"00": 512, "11": 512}
        },
        "execution_time_ms": 14.2
    }
```

---

## 💻 Workbench Command System

| Command | Action / Subsystem | Expected Output |
| :--- | :--- | :--- |
| `help` | Command Index | Full workbench manual and usage reference |
| `init` | Module Discovery | Scans `backend/modules/` and reports real status for all 4 slots |
| `system --info` | Hardware Telemetry | Host OS, CPU cores, RAM, and GPU detection |
| `cudaq --status` | CUDA-Q Inspection | Current target (`qpp-cpu`, `nvidia`) and availability |
| `cudaq --run` | CUDA-Q Simulation | Executes Bell state circuit and displays measurement histogram |
| `qiskit --status` | Qiskit Diagnostics | Qiskit version and IBM Quantum API token status |
| `qiskit --connect` | Connectivity Probe | Verifies local CPU simulator and remote IBM endpoint |
| `qiskit --run` | Qiskit Execution | Simulates Bell-state circuit via CPU Statevector sampler |
| `nvqlink --status` | NVQLink Telemetry | GPU-QPU coherent memory fabric parameters (900 GB/s) |
| `nvqlink --simulate` | Multi-Stage Test | Zero-copy VRAM staging, real-time feedback loop, latency metrics |
| `shor --status` | Shor Diagnostics | Quantum order-finding engine and register allocation |
| `shor --factor 15` | Shor Factoring | Mathematically decomposes $N = 15 \to 3 \times 5$ with order finding |
| `clear` | Terminal Refresh | Clears screen and resets prompt |
| `exit` | Graceful Shutdown | Terminates active terminal session |

---

## 📁 Project Structure

```
QUANTUM-OPS/
├── frontend/
│   ├── index.html                 # Cyberpunk terminal interface
│   ├── package.json               # Frontend dependencies (vite, xterm)
│   └── src/
│       ├── main.js                # HUD orchestration and telemetry sync
│       ├── terminal.js            # xterm.js shell, prompt, and command dispatcher
│       ├── commands.js            # Tab completion & command registry
│       └── style.css              # Cyberpunk black (#050505), green (#00FF41), scanlines
│
├── backend/
│   ├── main.py                    # FastAPI server & static file hosting
│   ├── command_handler.py         # Shell command parser & ANSI formatters
│   ├── module_registry.py         # Dynamic loader, isolation, contract validation
│   ├── schemas.py                 # Pydantic contract definitions
│   ├── system_info.py             # Telemetry service
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── cudaq_engine.py        # [Bhuwin] CUDA-Q CPU/GPU engine
│   │   ├── qiskit_connectivity.py # [DSP] Qiskit local simulation & IBM API
│   │   ├── nvqlink_demo.py        # [Yuva Sekhar] NVQLink architecture simulation
│   │   └── shors_algorithm.py     # [Nikihil] Shor's quantum factoring (N=15)
│   ├── services/
│   │   ├── execution_manager.py   # ThreadPool simulation dispatcher
│   │   └── hardware_detector.py   # Safe CPU, RAM & GPU probing
│   └── utils/
│       ├── logger.py              # Structured neon logger
│       └── results.py             # ANSI histograms, tables, and ASCII badges
│
├── tests/
│   ├── test_api.py                # FastAPI endpoint tests
│   ├── test_commands.py           # Command parsing & suggestions tests
│   └── test_modules.py            # Module contract compliance & algorithm tests
│
├── .env.example                   # Environment configuration template
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Python package dependencies
├── Dockerfile                     # Multi-arch Linux CPU/GPU Dockerfile
├── docker-compose.yml             # Docker Compose (CPU default, GPU profile)
└── README.md                      # Complete system documentation
```

---

## ⚡ Quickstart Guide

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13
- Git

### 2. Local Setup
```bash
# Clone the repository
git clone https://github.com/Bhuwinrag/Quantum-4-Ops.git
cd Quantum-4-Ops

# Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Launch the Workbench
```bash
# Start FastAPI server (serves both API and Cyberpunk Terminal UI)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser to: **`http://localhost:8000`**

---

## 🧪 Running Automated Tests

Run the full automated pytest suite:
```bash
pytest -v
```
All 20 tests verify API health, system telemetry, command routing, contract enforcement, and quantum algorithm math.

---

## 🐳 Docker Deployment

### Standard CPU Deployment (Default)
```bash
docker compose up quantum-ops-cpu --build
```
Access the application at `http://localhost:8000`.

### Optional GPU-Accelerated Deployment (NVIDIA GPU Host)
```bash
docker compose --profile gpu up quantum-ops-gpu
```

---

## 🤝 Contributor Workflow for Teammates

### Step 1: Clone and checkout your feature branch
```bash
git checkout -b feature/<your-module>
# Example: git checkout -b feature/qiskit
```

### Step 2: Edit your target file in `backend/modules/`
Ensure your file exports `get_status() -> dict` and `run(payload: dict) -> dict`.

### Step 3: Run the test suite
```bash
pytest tests/test_modules.py -v
```

### Step 4: Commit and push
```bash
git add backend/modules/<your_file>.py
git commit -m "feat(<module>): implement verified quantum logic"
git push origin feature/<your-module>
```
Submit a Pull Request to `main`. Bhuwin will review and merge!

