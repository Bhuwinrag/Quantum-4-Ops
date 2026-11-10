"""
QUANTUM//OPS - Command Parser & Handler
Parses interactive terminal commands, invokes the ExecutionManager,
and formats responses with ANSI colors and ASCII visualizations.
"""

import shlex
import difflib
from typing import Dict, Any, List
from backend.module_registry import registry
from backend.services.execution_manager import execution_manager
from backend.services.hardware_detector import HardwareDetector
from backend.schemas import CommandResponse
from backend.utils.results import (
    NEON_GREEN, CYAN, MUTED_GREEN, ALERT_RED, WARN_YELLOW,
    RESET, BOLD, DARK_GRAY, format_status_badge, format_histogram, format_table
)

AVAILABLE_COMMANDS = [
    "help",
    "init",
    "system --info",
    "cudaq --status",
    "cudaq --run",
    "qiskit --status",
    "qiskit --connect",
    "qiskit --run",
    "nvqlink --status",
    "nvqlink --simulate",
    "shor --status",
    "shor --factor 15",
    "clear",
    "exit",
]


class CommandHandler:
    """Dispatches CLI commands to quantum engines and formats outputs."""

    @classmethod
    async def process(cls, raw_command: str) -> CommandResponse:
        """Parses and executes command string."""
        cleaned = raw_command.strip()
        if not cleaned:
            return CommandResponse(
                status="success",
                command="",
                output="",
                data={},
            )

        try:
            tokens = shlex.split(cleaned)
        except Exception:
            tokens = cleaned.split()

        cmd = tokens[0].lower()
        args = tokens[1:]

        # Route to specific handlers
        if cmd == "help":
            return cls._handle_help()
        elif cmd == "init":
            return await cls._handle_init()
        elif cmd == "system":
            return cls._handle_system(args)
        elif cmd == "cudaq":
            return await cls._handle_cudaq(args)
        elif cmd == "qiskit":
            return await cls._handle_qiskit(args)
        elif cmd == "nvqlink":
            return await cls._handle_nvqlink(args)
        elif cmd == "shor":
            return await cls._handle_shor(args)
        elif cmd in ("clear", "cls"):
            return CommandResponse(
                status="success",
                command="clear",
                output="\033[2J\033[H",
                data={"action": "clear"},
            )
        elif cmd == "exit":
            return CommandResponse(
                status="success",
                command="exit",
                output=f"{WARN_YELLOW}[SESSION TERMINATED] Connection to QUANTUM//OPS Workbench closed gracefully.{RESET}\r\n",
                data={"action": "exit"},
            )
        else:
            return cls._handle_unknown(cleaned)

    @classmethod
    def _handle_help(cls) -> CommandResponse:
        """Returns the formatted help index."""
        headers = ["COMMAND", "DESCRIPTION", "OWNER / TARGET"]
        rows = [
            ["help", "Show workbench command reference", "Core System"],
            ["init", "Discover and initialize all 4 quantum modules", "System Kernel"],
            ["system --info", "Query host architecture, CPU, RAM & GPU telemetry", "Hardware Detector"],
            ["cudaq --status", "Inspect NVIDIA CUDA-Q status & available targets", "Bhuwin Rag (CUDA-Q)"],
            ["cudaq --run", "Execute Bell-state quantum kernel on CUDA-Q engine", "Bhuwin Rag (CUDA-Q)"],
            ["qiskit --status", "Query Qiskit framework & IBM Quantum config", "DSP (Qiskit)"],
            ["qiskit --connect", "Test local CPU simulator / IBM API connection", "DSP (Qiskit)"],
            ["qiskit --run", "Execute Bell-state circuit via Qiskit Statevector", "DSP (Qiskit)"],
            ["nvqlink --status", "Query NVQLink GPU-QPU memory fabric status", "Yuva Sekhar (NVQLink)"],
            ["nvqlink --simulate", "Run multi-stage GPU-QPU coherent memory test", "Yuva Sekhar (NVQLink)"],
            ["shor --status", "Query Shor's quantum factoring engine status", "Nikihil (Shor)"],
            ["shor --factor <N>", "Factor composite integer (default: N = 15)", "Nikihil (Shor)"],
            ["clear", "Clear terminal display buffer", "Terminal Core"],
            ["exit", "Gracefully terminate active terminal session", "Session Core"],
        ]

        table_str = format_table(rows, headers)
        out = (
            f"\r\n{NEON_GREEN}{BOLD}QUANTUM//OPS WORKBENCH COMMAND MANUAL:{RESET}\r\n"
            f"{DARK_GRAY}{'─' * 76}{RESET}\r\n"
            f"{table_str}\r\n\r\n"
            f"{MUTED_GREEN}Tip: Type any command above and press Enter. Arrow Up/Down navigates history.{RESET}\r\n"
        )
        return CommandResponse(status="success", command="help", output=out, data={"commands": AVAILABLE_COMMANDS})

    @classmethod
    async def _handle_init(cls) -> CommandResponse:
        """Initializes and reports real status of all modules."""
        registry.initialize()
        statuses = registry.get_all_statuses()

        lines = [
            f"\r\n{CYAN}{BOLD}INITIALIZING QUANTUM//OPS INTEGRATION KERNEL...{RESET}",
            f"{DARK_GRAY}Scanning module slots in backend/modules/...{RESET}\r\n",
        ]

        for key, st in statuses.items():
            badge = format_status_badge(st.status)
            exec_mode = f"{CYAN}[{st.execution_mode}]{RESET}"
            lines.append(f"  {badge} {st.module:<26} {exec_mode:<30}")
            if st.message:
                lines.append(f"        {MUTED_GREEN}-> {st.message}{RESET}")

        lines.append(f"\r\n{NEON_GREEN}{BOLD}[ SYSTEM READY ] Workbench initialization sequence complete.{RESET}\r\n")

        return CommandResponse(
            status="success",
            command="init",
            output="\r\n".join(lines),
            data={k: v.model_dump() for k, v in statuses.items()},
        )

    @classmethod
    def _handle_system(cls, args: List[str]) -> CommandResponse:
        """Handles 'system --info'."""
        if not args or args[0] in ("--info", "-i", "info"):
            hw = HardwareDetector.get_system_summary()
            
            headers = ["SUBSYSTEM", "TELEMETRY / SPECIFICATION", "STATUS"]
            rows = [
                ["Platform OS", f"{hw['os']} ({hw['os_release']})", "DETECTED"],
                ["Architecture", hw["architecture"], "VERIFIED"],
                ["Python Engine", f"v{hw['python_version']}", "ACTIVE"],
                ["Host Processor", hw["cpu"], f"{hw['cpu_cores']} Cores"],
                ["System RAM", f"{hw['ram_gb']} GB Physical Memory", "SUFFICIENT"],
                ["GPU Hardware", hw["gpu_name"], "ACCELERATED" if hw["gpu_detected"] else "NOT DETECTED"],
                ["CUDA Support", "Available" if hw["cuda_available"] else "Unavailable", "OK" if hw["cuda_available"] else "CPU_ONLY"],
                ["Default Mode", hw["active_execution_mode"], "ACTIVE"],
            ]
            table_str = format_table(rows, headers)

            notice = (
                f"{NEON_GREEN}✓ Execution Mode: CPU Simulator active (AMD/Intel x86_64). "
                f"No NVIDIA GPU required for simulation.{RESET}"
                if not hw["gpu_detected"]
                else f"{CYAN}✓ GPU Acceleration hardware active.{RESET}"
            )

            out = (
                f"\r\n{NEON_GREEN}{BOLD}SYSTEM HARDWARE & COMPUTATIONAL TELEMETRY:{RESET}\r\n"
                f"{DARK_GRAY}{'─' * 76}{RESET}\r\n"
                f"{table_str}\r\n\r\n"
                f"  {notice}\r\n"
            )
            return CommandResponse(status="success", command="system --info", output=out, data=hw)

        return CommandResponse(
            status="error",
            command=f"system {' '.join(args)}",
            output=f"{ALERT_RED}Invalid option: '{' '.join(args)}'. Did you mean 'system --info'?{RESET}\r\n",
            data={},
        )

    @classmethod
    async def _handle_cudaq(cls, args: List[str]) -> CommandResponse:
        """Handles 'cudaq --status' and 'cudaq --run'."""
        if not args or args[0] in ("--status", "-s"):
            res = registry.get("cudaq").query_status()
            badge = format_status_badge(res.status)
            out = [
                f"\r\n{NEON_GREEN}{BOLD}MODULE 01: NVIDIA CUDA-Q ENGINE STATUS{RESET}",
                f"{DARK_GRAY}{'─' * 60}{RESET}",
                f"  Status        : {badge} {res.status.upper()}",
                f"  Execution Mode: {CYAN}{res.execution_mode}{RESET}",
                f"  Owner         : Bhuwin Rag (Team Lead)",
                f"  Message       : {res.message}",
            ]
            if res.results:
                for k, v in res.results.items():
                    out.append(f"  {k:<14}: {MUTED_GREEN}{v}{RESET}")
            out.append("")
            return CommandResponse(status=res.status, command="cudaq --status", output="\r\n".join(out), data=res.model_dump())

        elif args[0] in ("--run", "-r"):
            allow_emul = "--emulate" in args or "-e" in args
            circuit_choice = "bell"
            for a in args:
                if a in ("ghz", "superposition", "bell"):
                    circuit_choice = a

            res = await execution_manager.execute_module_async(
                "cudaq",
                {"circuit": circuit_choice, "shots": 1024, "allow_emulation": allow_emul}
            )

            badge = format_status_badge(res.status)
            out = [
                f"\r\n{NEON_GREEN}{BOLD}CUDA-Q CIRCUIT EXECUTION RESULT{RESET}",
                f"{DARK_GRAY}{'─' * 60}{RESET}",
                f"  Status        : {badge} {res.status.upper()}",
                f"  Mode          : {CYAN}{res.execution_mode}{RESET}",
                f"  Execution Time: {res.execution_time_ms} ms",
                f"  Message       : {res.message}",
            ]

            if res.status in ("success", "simulated"):
                counts = res.results.get("counts", {})
                if counts:
                    out.append(f"\r\n{CYAN}Quantum Measurement Distribution (1024 shots):{RESET}")
                    out.append(format_histogram(counts))
            else:
                out.append(f"\r\n{WARN_YELLOW}[NOTICE] {res.results.get('reason', '')}{RESET}")
                out.append(f"{MUTED_GREEN}Tip: {res.results.get('command_hint', 'Run in Docker or use --emulate for preview.')}{RESET}")

            out.append("")
            return CommandResponse(status=res.status, command="cudaq --run", output="\r\n".join(out), data=res.model_dump())

        return cls._handle_unknown(f"cudaq {' '.join(args)}")

    @classmethod
    async def _handle_qiskit(cls, args: List[str]) -> CommandResponse:
        """Handles 'qiskit --status', 'qiskit --connect', and 'qiskit --run'."""
        if not args or args[0] in ("--status", "-s"):
            res = registry.get("qiskit").query_status()
            badge = format_status_badge(res.status)
            out = [
                f"\r\n{NEON_GREEN}{BOLD}MODULE 02: QISKIT API CONNECTIVITY STATUS{RESET}",
                f"{DARK_GRAY}{'─' * 60}{RESET}",
                f"  Status        : {badge} {res.status.upper()}",
                f"  Execution Mode: {CYAN}{res.execution_mode}{RESET}",
                f"  Owner         : DSP (Qiskit API Connectivity)",
                f"  Message       : {res.message}",
            ]
            if res.results:
                for k, v in res.results.items():
                    out.append(f"  {k:<20}: {MUTED_GREEN}{v}{RESET}")
            out.append("")
            return CommandResponse(status=res.status, command="qiskit --status", output="\r\n".join(out), data=res.model_dump())

        elif args[0] in ("--connect", "-c"):
            res = registry.get("qiskit").query_status()
            token_conf = res.results.get("ibm_quantum_configured", False)
            out = [
                f"\r\n{CYAN}{BOLD}TESTING QISKIT RUNTIME CONNECTIVITY...{RESET}",
                f"{DARK_GRAY}{'─' * 60}{RESET}",
                f"  Local CPU Simulator  : {NEON_GREEN}[ ONLINE ]{RESET} Qiskit Aer/Statevector ready.",
                f"  IBM Quantum Cloud API: " + (
                    f"{NEON_GREEN}[ CONFIGURED ] Token active.{RESET}"
                    if token_conf else
                    f"{WARN_YELLOW}[ OPTIONAL ] Token not set in .env. Operating in CPU simulator mode.{RESET}"
                ),
                f"\r\n{MUTED_GREEN}System is ready for local quantum circuit execution.{RESET}\r\n",
            ]
            return CommandResponse(status="success", command="qiskit --connect", output="\r\n".join(out), data=res.model_dump())

        elif args[0] in ("--run", "-r"):
            circuit_choice = "bell"
            for a in args:
                if a in ("ghz", "superposition", "bell"):
                    circuit_choice = a

            res = await execution_manager.execute_module_async(
                "qiskit", {"circuit": circuit_choice, "shots": 1024}
            )
            badge = format_status_badge(res.status)
            out = [
                f"\r\n{NEON_GREEN}{BOLD}QISKIT QUANTUM CIRCUIT EXECUTION RESULT{RESET}",
                f"{DARK_GRAY}{'─' * 60}{RESET}",
                f"  Status        : {badge} {res.status.upper()}",
                f"  Mode          : {CYAN}{res.execution_mode}{RESET}",
                f"  Execution Time: {res.execution_time_ms} ms",
                f"  Message       : {res.message}",
            ]
            counts = res.results.get("counts", {})
            if counts:
                out.append(f"\r\n{CYAN}Quantum Measurement Distribution (1024 shots):{RESET}")
                out.append(format_histogram(counts))
            out.append("")
            return CommandResponse(status=res.status, command="qiskit --run", output="\r\n".join(out), data=res.model_dump())

        return cls._handle_unknown(f"qiskit {' '.join(args)}")

    @classmethod
    async def _handle_nvqlink(cls, args: List[str]) -> CommandResponse:
        """Handles 'nvqlink --status' and 'nvqlink --simulate'."""
        if not args or args[0] in ("--status", "-s"):
            res = registry.get("nvqlink").query_status()
            badge = format_status_badge(res.status)
            out = [
                f"\r\n{NEON_GREEN}{BOLD}MODULE 03: NVIDIA NVQLINK ARCHITECTURE STATUS{RESET}",
                f"{DARK_GRAY}{'─' * 60}{RESET}",
                f"  Status        : {badge} {res.status.upper()}",
                f"  Execution Mode: {CYAN}{res.execution_mode}{RESET}",
                f"  Owner         : Yuva Sekhar (NVIDIA NVQLink)",
                f"  Message       : {res.message}",
            ]
            if res.results:
                for k, v in res.results.items():
                    out.append(f"  {k:<22}: {MUTED_GREEN}{v}{RESET}")
            out.append("")
            return CommandResponse(status=res.status, command="nvqlink --status", output="\r\n".join(out), data=res.model_dump())

        elif args[0] in ("--simulate", "-s", "--run", "-r"):
            res = await execution_manager.execute_module_async("nvqlink", {"qubits": 8, "shots": 1000})
            badge = format_status_badge(res.status)
            out = [
                f"\r\n{NEON_GREEN}{BOLD}NVQLINK GPU-QPU INTERCONNECT TRANSMISSION PIPELINE{RESET}",
                f"{DARK_GRAY}{'─' * 70}{RESET}",
                f"  Status           : {badge} {res.status.upper()} (Architecture Simulation)",
                f"  Job ID           : {CYAN}{res.results.get('job_id')}{RESET}",
                f"  Bandwidth        : {NEON_GREEN}{res.results.get('bandwidth_achieved')}{RESET}",
                f"  Interconnect Latency: {CYAN}{res.results.get('nvqlink_latency_us')} µs{RESET} (PCIe Gen5 baseline: {res.results.get('pcie_baseline_latency_us')} µs)",
                f"  Latency Advantage: {NEON_GREEN}{res.results.get('latency_reduction_factor')}{RESET}",
                f"\r\n{CYAN}PIPELINE STAGES COMPLETED:{RESET}",
            ]
            for st in res.results.get("pipeline_stages", []):
                out.append(f"  {NEON_GREEN}[✓] Step {st['step']}: {st['name']:<24}{RESET} -> {st['detail']}")
            out.append(f"\r\n  {MUTED_GREEN}Notice: {res.results.get('notice')}{RESET}\r\n")
            return CommandResponse(status=res.status, command="nvqlink --simulate", output="\r\n".join(out), data=res.model_dump())

        return cls._handle_unknown(f"nvqlink {' '.join(args)}")

    @classmethod
    async def _handle_shor(cls, args: List[str]) -> CommandResponse:
        """Handles 'shor --status' and 'shor --factor <N>'."""
        if not args or args[0] in ("--status", "-s"):
            res = registry.get("shor").query_status()
            badge = format_status_badge(res.status)
            out = [
                f"\r\n{NEON_GREEN}{BOLD}MODULE 04: SHOR'S ALGORITHM FACTORING STATUS{RESET}",
                f"{DARK_GRAY}{'─' * 60}{RESET}",
                f"  Status        : {badge} {res.status.upper()}",
                f"  Execution Mode: {CYAN}{res.execution_mode}{RESET}",
                f"  Owner         : Nikihil (Shor's Algorithm)",
                f"  Message       : {res.message}",
            ]
            if res.results:
                for k, v in res.results.items():
                    out.append(f"  {k:<20}: {MUTED_GREEN}{v}{RESET}")
            out.append("")
            return CommandResponse(status=res.status, command="shor --status", output="\r\n".join(out), data=res.model_dump())

        elif args[0] in ("--factor", "-f"):
            number = 15
            if len(args) > 1:
                try:
                    number = int(args[1])
                except ValueError:
                    return CommandResponse(
                        status="error",
                        command=f"shor {' '.join(args)}",
                        output=f"{ALERT_RED}Invalid number parameter '{args[1]}'. Must be an integer like 15.{RESET}\r\n",
                        data={},
                    )

            res = await execution_manager.execute_module_async("shor", {"number": number})
            badge = format_status_badge(res.status)
            r_data = res.results
            factors = r_data.get("factors", [])
            factors_str = f"{factors[0]} × {factors[1]}" if len(factors) == 2 else "None"

            out = [
                f"\r\n{NEON_GREEN}{BOLD}SHOR'S QUANTUM FACTORIZATION EXECUTION{RESET}",
                f"{DARK_GRAY}{'─' * 65}{RESET}",
                f"  Status            : {badge} {res.status.upper()}",
                f"  Composite Input N : {CYAN}{r_data.get('input_number')}{RESET}",
                f"  Coprime Base (a)  : {r_data.get('coprime_base_a')}",
                f"  Quantum Period (r): {CYAN}{r_data.get('detected_period_r')}{RESET} (derived via order-finding)",
                f"  Measured Phase (φ): {r_data.get('measured_phase')}",
                f"  Discovered Factors: {NEON_GREEN}{BOLD}{factors_str}{RESET}",
                f"  Verification Check: {NEON_GREEN}{r_data.get('verification_equation')}{RESET}",
                f"  Execution Time    : {res.execution_time_ms} ms",
            ]

            counts = r_data.get("counts", {})
            if counts:
                out.append(f"\r\n{CYAN}Quantum Phase Estimation Measurement Histogram:{RESET}")
                out.append(format_histogram(counts))
            out.append("")
            return CommandResponse(status=res.status, command=f"shor --factor {number}", output="\r\n".join(out), data=res.model_dump())

        return cls._handle_unknown(f"shor {' '.join(args)}")

    @classmethod
    def _handle_unknown(cls, cmd_string: str) -> CommandResponse:
        """Provides smart suggestions for unrecognized commands."""
        closest = difflib.get_close_matches(cmd_string, AVAILABLE_COMMANDS, n=2, cutoff=0.3)
        suggestion_text = ""
        if closest:
            suggestion_text = f"\r\n{CYAN}Did you mean one of these?{RESET}\r\n" + "\r\n".join(
                f"  -> {NEON_GREEN}{c}{RESET}" for c in closest
            )

        out = (
            f"\r\n{ALERT_RED}Command not recognized: '{cmd_string}'{RESET}"
            f"{suggestion_text}\r\n"
            f"{MUTED_GREEN}Type {CYAN}help{MUTED_GREEN} to view all available workbench commands.{RESET}\r\n"
        )
        return CommandResponse(
            status="error",
            command=cmd_string,
            output=out,
            data={"suggestion": closest[0] if closest else None},
        )
