"""
QUANTUM//OPS - Hardware & Platform Detector
Safely probes CPU, RAM, OS, and GPU hardware without crashing on CPU-only systems.
"""

import os
import platform
import subprocess
import shutil
from typing import Dict, Any, Optional
from backend.utils.logger import logger


class HardwareDetector:
    """Safe hardware probing service with zero assumptions about GPU hardware."""

    @staticmethod
    def get_cpu_info() -> Dict[str, Any]:
        """Detects processor information."""
        cpu_model = platform.processor() or "AMD/Intel x86_64 Processor"
        cpu_cores = os.cpu_count() or 4
        
        # On Windows, registry or wmic might offer cleaner processor names
        if platform.system() == "Windows":
            try:
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
                )
                cpu_model = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
                winreg.CloseKey(key)
            except Exception:
                pass

        return {
            "model": cpu_model,
            "cores": cpu_cores,
            "arch": platform.machine(),
        }

    @staticmethod
    def get_memory_info() -> float:
        """Returns total RAM in Gigabytes (GB)."""
        ram_gb = 16.0  # safe default fallback
        
        if platform.system() == "Windows":
            try:
                import ctypes
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]
                stat = MEMORYSTATUSEX()
                stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
                ram_gb = round(stat.ullTotalPhys / (1024 ** 3), 2)
            except Exception as e:
                logger.debug(f"Windows RAM probe fallback: {e}")
        elif platform.system() == "Linux":
            try:
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if "MemTotal" in line:
                            total_kb = int(line.split()[1])
                            ram_gb = round(total_kb / (1024 ** 2), 2)
                            break
            except Exception as e:
                logger.debug(f"Linux RAM probe fallback: {e}")

        return ram_gb

    @staticmethod
    def detect_gpu() -> Dict[str, Any]:
        """
        Safely inspects system for NVIDIA GPU acceleration.
        Returns empty detection if none present; does NOT throw exceptions.
        """
        gpu_detected = False
        gpu_name: Optional[str] = None
        cuda_available = False

        # 1. Check if nvidia-smi exists in PATH
        smi_path = shutil.which("nvidia-smi")
        if smi_path:
            try:
                res = subprocess.run(
                    ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if res.returncode == 0 and res.stdout.strip():
                    gpu_name = res.stdout.strip().split(",")[0]
                    gpu_detected = True
                    cuda_available = True
            except Exception as e:
                logger.debug(f"nvidia-smi execution error: {e}")

        # 2. Check PyTorch CUDA if installed
        if not gpu_detected:
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_detected = True
                    cuda_available = True
                    gpu_name = torch.cuda.get_device_name(0)
            except Exception:
                pass

        # 3. Check CUDA-Q if installed
        if not gpu_detected:
            try:
                import cudaq
                if cudaq.has_target("nvidia"):
                    gpu_detected = True
                    cuda_available = True
                    gpu_name = "NVIDIA CUDA-Q GPU Target"
            except Exception:
                pass

        return {
            "gpu_detected": gpu_detected,
            "gpu_name": gpu_name if gpu_detected else "None (CPU Execution Only)",
            "cuda_available": cuda_available,
        }

    @classmethod
    def get_system_summary(cls) -> Dict[str, Any]:
        """Provides an aggregated hardware profile."""
        cpu = cls.get_cpu_info()
        ram = cls.get_memory_info()
        gpu = cls.detect_gpu()

        active_mode = "gpu_simulator" if gpu["cuda_available"] else "cpu_simulator"

        return {
            "os": platform.system(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "cpu": cpu["model"],
            "cpu_cores": cpu["cores"],
            "ram_gb": ram,
            "gpu_detected": gpu["gpu_detected"],
            "gpu_name": gpu["gpu_name"],
            "cuda_available": gpu["cuda_available"],
            "active_execution_mode": active_mode,
        }

