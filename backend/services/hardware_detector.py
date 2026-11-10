"""
QUANTUM//OPS - Hardware & Platform Detector
Safely probes CPU, RAM, OS, and actively detects NVIDIA RTX GPUs across multiple probe vectors.
"""

import os
import platform
import subprocess
import shutil
import ctypes
from typing import Dict, Any, Optional
from backend.utils.logger import logger


class HardwareDetector:
    """Safe hardware probing service with active NVIDIA GPU auto-detection."""

    @staticmethod
    def get_cpu_info() -> Dict[str, Any]:
        """Detects processor information."""
        cpu_model = platform.processor() or "x86_64 Processor"
        cpu_cores = os.cpu_count() or 4
        
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
        ram_gb = 16.0
        
        if platform.system() == "Windows":
            try:
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
        Actively detects NVIDIA GPUs (RTX 30-series, RTX 40-series, Quadro, etc.)
        across 4 independent discovery vectors.
        """
        gpu_detected = False
        gpu_name: Optional[str] = None
        cuda_available = False
        vram_gb: Optional[float] = None

        # 1. Direct Driver DLL (nvcuda.dll on Windows / libcuda.so on Linux)
        lib_candidates = ["nvcuda.dll", "nvcuda", "libcuda.so", "libcuda.so.1"]
        for lib in lib_candidates:
            try:
                if hasattr(ctypes, "windll"):
                    cuda = ctypes.windll.LoadLibrary(lib)
                else:
                    cuda = ctypes.CDLL(lib)
                
                if cuda.cuInit(0) == 0:
                    dev = ctypes.c_int()
                    if cuda.cuDeviceGet(ctypes.byref(dev), 0) == 0:
                        name_buf = ctypes.create_string_buffer(256)
                        cuda.cuDeviceGetName(name_buf, 256, dev)
                        detected = name_buf.value.decode("utf-8").strip()
                        if detected:
                            gpu_name = detected
                            gpu_detected = True
                            cuda_available = True
                            mem = ctypes.c_size_t()
                            if hasattr(cuda, "cuDeviceTotalMem"):
                                if cuda.cuDeviceTotalMem(ctypes.byref(mem), dev) == 0:
                                    vram_gb = round(mem.value / (1024 ** 3), 2)
                            break
            except Exception:
                pass

        # 2. nvidia-smi command query
        if not gpu_detected:
            smi_paths = [
                shutil.which("nvidia-smi"),
                r"C:\Windows\System32\nvidia-smi.exe",
                r"C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe",
            ]
            for smi in filter(None, smi_paths):
                if os.path.isfile(smi):
                    try:
                        res = subprocess.run(
                            [smi, "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                            capture_output=True,
                            text=True,
                            timeout=3,
                        )
                        if res.returncode == 0 and res.stdout.strip():
                            parts = res.stdout.strip().split("\n")[0].split(",")
                            gpu_name = parts[0].strip()
                            gpu_detected = True
                            cuda_available = True
                            if len(parts) > 1:
                                try:
                                    vram_gb = round(float(parts[1].strip()) / 1024, 2)
                                except Exception:
                                    pass
                            break
                    except Exception:
                        pass

        # 3. Windows WMI Display Adapters
        if not gpu_detected and platform.system() == "Windows":
            try:
                res = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                if res.returncode == 0:
                    lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
                    for line in lines:
                        if any(k in line.upper() for k in ["NVIDIA", "GEFORCE", "RTX", "QUADRO", "TESLA"]):
                            gpu_name = line
                            gpu_detected = True
                            cuda_available = True
                            break
            except Exception:
                pass

        # 4. PyTorch / CuPy fallback
        if not gpu_detected:
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_detected = True
                    cuda_available = True
                    gpu_name = torch.cuda.get_device_name(0)
            except Exception:
                pass

        return {
            "gpu_detected": gpu_detected,
            "gpu_name": gpu_name if gpu_detected else "None (CPU Execution Only)",
            "cuda_available": cuda_available,
            "vram_gb": vram_gb,
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
            "vram_gb": gpu.get("vram_gb"),
            "active_execution_mode": active_mode,
        }
