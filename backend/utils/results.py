"""
QUANTUM//OPS - Result Formatting Utilities
ANSI colors and ASCII layout generators for hacker-style terminal responses.
"""

from typing import Dict, Any, List

# ANSI Color constants
ESC = "\033["
RESET = f"{ESC}0m"
BOLD = f"{ESC}1m"
DIM = f"{ESC}2m"
ITALIC = f"{ESC}3m"
UNDERLINE = f"{ESC}4m"

# Cyber theme palette
NEON_GREEN = f"{ESC}38;2;0;255;65m"
CYAN = f"{ESC}38;2;0;255;255m"
MUTED_GREEN = f"{ESC}38;2;85;122;95m"
DARK_GRAY = f"{ESC}38;2;70;70;70m"
BRIGHT_WHITE = f"{ESC}38;2;240;255;240m"
ALERT_RED = f"{ESC}38;2;255;75;75m"
WARN_YELLOW = f"{ESC}38;2;255;215;0m"


def get_boot_banner() -> str:
    """Returns the authentic QUANTUM//OPS ASCII banner."""
    lines = [
        f"{NEON_GREEN} ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗████████╗██╗   ██╗███╗   ███╗    ██████╗ ██████╗ ███████╗{RESET}",
        f"{NEON_GREEN}██╔═══██╗██║   ██║██╔══██╗████╗  ██║╚══██╔══╝██║   ██║████╗ ████║   ██╔═══██╗██╔══██╗██╔════╝{RESET}",
        f"{NEON_GREEN}██║   ██║██║   ██║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║   ██║   ██║██████╔╝███████╗{RESET}",
        f"{NEON_GREEN}██║▄▄ ██║██║   ██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║   ██║   ██║██╔═══╝ ╚════██║{RESET}",
        f"{NEON_GREEN}╚██████╔╝╚██████╔╝██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║██╗╚██████╔╝██║     ███████║{RESET}",
        f"{NEON_GREEN} ╚══▀▀═╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚══════╝{RESET}",
        f"{CYAN}       QUANTUM HYBRID COMPUTING WORKBENCH  ::  v1.0.0-PROD{RESET}",
        f"{DARK_GRAY}--------------------------------------------------------------------------------{RESET}",
    ]
    return "\r\n".join(lines)


def format_status_badge(status: str) -> str:
    """Returns a colorized status badge."""
    st = status.lower()
    if st in ("ok", "success", "online", "ready"):
        return f"{NEON_GREEN}[ OK ]{RESET}"
    elif st in ("sim", "simulated", "simulation"):
        return f"{CYAN}[ SIM ]{RESET}"
    elif st in ("warn", "warning"):
        return f"{WARN_YELLOW}[ WARN ]{RESET}"
    elif st in ("info", "initializing"):
        return f"{CYAN}[ INFO ]{RESET}"
    elif st in ("unavailable", "error", "failed"):
        return f"{ALERT_RED}[ FAIL ]{RESET}"
    return f"{MUTED_GREEN}[ {status.upper()} ]{RESET}"


def format_histogram(counts: Dict[str, int], width: int = 28) -> str:
    """Renders an ASCII distribution histogram for quantum measurements."""
    if not counts:
        return f"{MUTED_GREEN}  (no measurement counts registered){RESET}"
    
    total = sum(counts.values()) or 1
    max_count = max(counts.values()) if counts else 1
    
    output = []
    output.append(f"{CYAN}  STATE    COUNTS    PROBABILITY    DISTRIBUTION{RESET}")
    output.append(f"{DARK_GRAY}  ────────────────────────────────────────────────────────────{RESET}")
    
    sorted_states = sorted(counts.keys())
    for state in sorted_states:
        c = counts[state]
        prob = (c / total) * 100
        bar_len = int((c / max_count) * width)
        bar = "█" * bar_len
        output.append(
            f"  {NEON_GREEN}|{state:>4}⟩{RESET}  {c:>6}d   {prob:>6.2f}%       {CYAN}{bar:<{width}}{RESET}"
        )
    return "\r\n".join(output)


def format_table(rows: List[List[str]], headers: List[str]) -> str:
    """Renders a cyberpunk styled table."""
    col_widths = [len(h) for h in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(str(cell)))
    
    lines = []
    header_str = "  ".join(
        f"{CYAN}{headers[i]:<{col_widths[i]}}{RESET}" for i in range(len(headers))
    )
    lines.append(header_str)
    
    sep_str = "  ".join(f"{DARK_GRAY}{'─' * col_widths[i]}{RESET}" for i in range(len(headers)))
    lines.append(sep_str)
    
    for row in rows:
        row_str = "  ".join(
            f"{BRIGHT_WHITE}{str(row[i]):<{col_widths[i]}}{RESET}" for i in range(len(row))
        )
        lines.append(row_str)
    
    return "\r\n".join(lines)
