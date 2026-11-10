"""
QUANTUM//OPS - Structured Logger
Provides formatted, colored logging for terminal and server events.
"""

import sys
import logging
from datetime import datetime

# ANSI Color codes for console output
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[38;2;0;255;65m"
CYAN = "\033[38;2;0;255;255m"
YELLOW = "\033[38;2;255;200;50m"
RED = "\033[38;2;255;70;70m"
MUTED = "\033[38;2;110;140;120m"


class QuantumFormatter(logging.Formatter):
    """Custom formatter with neon cyber styling."""

    LEVEL_COLORS = {
        logging.DEBUG: MUTED,
        logging.INFO: GREEN,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: f"{RED}{BOLD}",
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.LEVEL_COLORS.get(record.levelno, RESET)
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S.%f")[:-3]
        level_tag = f"[{record.levelname[:4]}]"
        
        message = record.getMessage()
        return f"{MUTED}{timestamp}{RESET} {color}{level_tag:<6}{RESET} {CYAN}{record.name}{RESET}: {message}"


def get_logger(name: str = "quantum_ops") -> logging.Logger:
    """Get or create a configured logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(QuantumFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


logger = get_logger("core")

