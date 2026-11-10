/**
 * QUANTUM//OPS - Frontend Command Registry & Autocompletion
 */

export const COMMAND_LIST = [
  "help",
  "init",
  "system --info",
  "cudaq --status",
  "cudaq --run",
  "cudaq --run ghz",
  "cudaq --run superposition",
  "qiskit --status",
  "qiskit --connect",
  "qiskit --run",
  "qiskit --run ghz",
  "nvqlink --status",
  "nvqlink --simulate",
  "shor --status",
  "shor --factor 15",
  "clear",
  "exit",
];

export const COMMAND_HELP = {
  "help": "Display workbench command reference",
  "init": "Run asynchronous module discovery & system verification",
  "system --info": "Inspect host hardware, CPU, RAM & GPU telemetry",
  "cudaq --status": "Query NVIDIA CUDA-Q platform status",
  "cudaq --run": "Execute CUDA-Q quantum kernel (Bell-state default)",
  "qiskit --status": "Query Qiskit local simulation & IBM API credentials",
  "qiskit --connect": "Test Qiskit CPU Statevector engine & IBM endpoint",
  "qiskit --run": "Execute circuit using Qiskit local statevector simulator",
  "nvqlink --status": "Query NVIDIA NVQLink coherent memory fabric status",
  "nvqlink --simulate": "Simulate multi-stage GPU-QPU memory transmission",
  "shor --status": "Query Shor's quantum factoring engine status",
  "shor --factor 15": "Execute Shor's quantum order-finding factorization for N = 15",
  "clear": "Clear terminal display buffer",
  "exit": "Close active terminal session gracefully",
};

/**
 * Returns matching command candidates for Tab completion
 */
export function getTabCompletions(currentInput) {
  if (!currentInput) return [];
  const lower = currentInput.toLowerCase();
  return COMMAND_LIST.filter(c => c.toLowerCase().startsWith(lower));
}

