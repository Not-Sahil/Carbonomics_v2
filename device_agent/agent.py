"""
Carbonomics v3 — Advanced Enterprise Device Agent
Cross-platform hardware telemetry daemon (Windows, Linux, macOS).
Collects CPU, Memory, Disk, GPU, Network, and thermal metrics.
Communicates securely via authenticated HTTP/REST with central Carbonomics backend.
"""

import argparse
import json
import os
import sys
import io
import time
import uuid
import platform
import signal
import threading
import socket
from datetime import datetime

if sys.platform == "win32":
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Hardware telemetry dependencies with graceful fallback
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Optional PyNVML for NVIDIA GPU telemetry
try:
    import pynvml
    pynvml.nvmlInit()
    NVML_AVAILABLE = True
except Exception:
    NVML_AVAILABLE = False

AGENT_VERSION = "3.0.0"
DEFAULT_SERVER = "http://localhost:5000"
HEARTBEAT_INTERVAL = 15  # seconds


class DeviceTelemetryAgent:
    """Hardware telemetry monitor and secure backend communicator"""

    def __init__(
        self,
        server_url: str = DEFAULT_SERVER,
        region: str = "ap-south-1",
        device_type: str = "laptop",
        device_name: str = None,
        department: str = "Engineering",
        interval: int = HEARTBEAT_INTERVAL
    ):
        self.server_url = server_url.rstrip("/")
        self.region = region
        self.device_type = device_type
        self.device_name = device_name or platform.node() or socket.gethostname()
        self.department = department
        self.interval = interval
        self.device_id, self.auth_token = self._load_or_create_identity()
        self._running = False
        self._thread = None
        self._prev_net_io = None
        self._prev_net_time = None

    def _load_or_create_identity(self):
        """Persist device ID and token in home directory"""
        home = os.path.expanduser("~")
        cred_path = os.path.join(home, ".carbonomics_device_auth.json")
        if os.path.exists(cred_path):
            try:
                with open(cred_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("device_id"), data.get("auth_token")
            except Exception:
                pass

        dev_id = f"DEV-{str(uuid.uuid4())[:8].upper()}"
        auth_tok = f"tok_{uuid.uuid4().hex}"
        try:
            with open(cred_path, "w", encoding="utf-8") as f:
                json.dump({"device_id": dev_id, "auth_token": auth_tok}, f, indent=2)
        except Exception:
            pass
        return dev_id, auth_tok

    def _get_gpu_metrics(self):
        """Read GPU utilization and memory if supported"""
        if not NVML_AVAILABLE:
            return {"gpu_util_pct": 0.0, "gpu_mem_used_mb": 0.0, "gpu_name": None}
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
            name = pynvml.nvmlDeviceGetName(handle)
            name_str = name.decode("utf-8") if isinstance(name, bytes) else str(name)
            return {
                "gpu_util_pct": float(util.gpu),
                "gpu_mem_used_mb": round(mem.used / (1024 ** 2), 1),
                "gpu_name": name_str
            }
        except Exception:
            return {"gpu_util_pct": 0.0, "gpu_mem_used_mb": 0.0, "gpu_name": None}

    def _get_network_rates(self):
        """Calculate real throughput in KB/s"""
        if not PSUTIL_AVAILABLE:
            return {"net_tx_kbs": 0.0, "net_rx_kbs": 0.0}
        try:
            curr_io = psutil.net_io_counters()
            curr_time = time.time()
            if self._prev_net_io and self._prev_net_time:
                dt = max(curr_time - self._prev_net_time, 0.1)
                tx_kbs = round((curr_io.bytes_sent - self._prev_net_io.bytes_sent) / dt / 1024.0, 1)
                rx_kbs = round((curr_io.bytes_recv - self._prev_net_io.bytes_recv) / dt / 1024.0, 1)
            else:
                tx_kbs, rx_kbs = 0.0, 0.0
            self._prev_net_io = curr_io
            self._prev_net_time = curr_time
            return {"net_tx_kbs": max(0.0, tx_kbs), "net_rx_kbs": max(0.0, rx_kbs)}
        except Exception:
            return {"net_tx_kbs": 0.0, "net_rx_kbs": 0.0}

    def _collect_top_processes(self, limit=5):
        """Collect sanitized top process statistics"""
        if not PSUTIL_AVAILABLE:
            return []
        try:
            procs = []
            for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                try:
                    info = p.info
                    if info["cpu_percent"] is not None:
                        # Exclude system arguments for privacy
                        procs.append({
                            "pid": info["pid"],
                            "name": info["name"] or "process",
                            "cpu_percent": round(info["cpu_percent"], 1),
                            "memory_percent": round(info.get("memory_percent") or 0.0, 1)
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            procs.sort(key=lambda x: x["cpu_percent"], reverse=True)
            return procs[:limit]
        except Exception:
            return []

    def collect(self):
        """Read full system state and hardware telemetry"""
        snapshot = {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "device_type": self.device_type,
            "region": self.region,
            "department": self.department,
            "agent_version": AGENT_VERSION,
            "os_name": platform.system(),
            "os_version": platform.version()[:60],
            "processor": platform.processor() or "Multi-Core CPU",
            "timestamp": datetime.utcnow().isoformat(),
        }

        if PSUTIL_AVAILABLE:
            try:
                snapshot["cpu_util_pct"] = round(psutil.cpu_percent(interval=0.3), 1)
                snapshot["cpu_count_logical"] = psutil.cpu_count(logical=True)
                snapshot["cpu_count_physical"] = psutil.cpu_count(logical=False)

                mem = psutil.virtual_memory()
                snapshot["memory_total_gb"] = round(mem.total / (1024 ** 3), 1)
                snapshot["memory_used_gb"] = round(mem.used / (1024 ** 3), 1)
                snapshot["memory_util_pct"] = round(mem.percent, 1)

                disk = psutil.disk_usage("/")
                snapshot["storage_total_gb"] = round(disk.total / (1024 ** 3), 1)
                snapshot["storage_used_gb"] = round(disk.used / (1024 ** 3), 1)
                snapshot["storage_util_pct"] = round(disk.percent, 1)

                boot_time = psutil.boot_time()
                snapshot["uptime_hours"] = round((time.time() - boot_time) / 3600.0, 2)

                bat = psutil.sensors_battery()
                if bat:
                    snapshot["battery_pct"] = bat.percent
                    snapshot["battery_charging"] = bat.power_plugged
                else:
                    snapshot["battery_pct"] = None
                    snapshot["battery_charging"] = True
            except Exception as e:
                snapshot["telemetry_error"] = str(e)
        else:
            # Fallback baseline
            snapshot["cpu_util_pct"] = 35.0
            snapshot["memory_total_gb"] = 16.0
            snapshot["memory_used_gb"] = 6.4
            snapshot["memory_util_pct"] = 40.0
            snapshot["storage_total_gb"] = 512.0
            snapshot["storage_used_gb"] = 210.0
            snapshot["storage_util_pct"] = 41.0
            snapshot["uptime_hours"] = 8.5

        # Merge GPU, network rates, and top processes
        snapshot.update(self._get_gpu_metrics())
        snapshot.update(self._get_network_rates())
        snapshot["top_processes"] = self._collect_top_processes(5)

        return snapshot

    def register(self):
        """Register device with backend using auth token"""
        if not REQUESTS_AVAILABLE:
            print("Warning: 'requests' library required for backend communication.")
            return False

        url = f"{self.server_url}/api/fleet/register"
        payload = self.collect()
        payload["auth_token"] = self.auth_token

        headers = {"Authorization": f"Bearer {self.auth_token}"}
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=6)
            if r.status_code in [200, 201]:
                print(f"[OK] Agent registered: {self.device_name} ({self.device_id}) at {self.server_url}")
                return True
            print(f"[WARN] Registration response: {r.status_code} - {r.text[:120]}")
            return False
        except Exception as e:
            print(f"[ERR] Cannot connect to central server {self.server_url}: {e}")
            return False

    def heartbeat(self):
        """Send periodic telemetry heartbeat"""
        if not REQUESTS_AVAILABLE:
            return
        url = f"{self.server_url}/api/fleet/heartbeat"
        payload = self.collect()
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                co2 = data.get("latest_daily_kg", 0.0)
                watts = data.get("power_watts", 0.0)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Heartbeat sent | CPU: {payload.get('cpu_util_pct')}% | Power: {watts:.1f}W | CO2: {co2:.4f} kg/day")
            elif r.status_code == 404:
                # Re-register if dropped
                self.register()
        except Exception as e:
            print(f"[WARN] Heartbeat dropped: {e}")

    def run_forever(self):
        """Start daemon loop with graceful SIGINT handling"""
        print(f"Starting Carbonomics v3 Agent v{AGENT_VERSION}...")
        self._running = True
        self.register()

        def handle_exit(signum, frame):
            print("\nShutting down device agent...")
            self._running = False
            sys.exit(0)

        signal.signal(signal.SIGINT, handle_exit)
        signal.signal(signal.SIGTERM, handle_exit)

        while self._running:
            time.sleep(self.interval)
            self.heartbeat()


def main():
    parser = argparse.ArgumentParser(description="Carbonomics v3 Enterprise Device Agent")
    parser.add_argument("--server", default=DEFAULT_SERVER, help="Backend URL (default: http://localhost:5000)")
    parser.add_argument("--region", default="ap-south-1", help="Grid region code (default: ap-south-1)")
    parser.add_argument("--device-type", default="laptop", choices=["laptop", "desktop", "workstation", "server_1u", "server_2u", "mini_pc", "raspberry_pi"], help="Hardware classification")
    parser.add_argument("--name", default=None, help="Friendly name of this machine")
    parser.add_argument("--department", default="Engineering", help="Assigned corporate department")
    parser.add_argument("--interval", type=int, default=HEARTBEAT_INTERVAL, help="Heartbeat period in seconds")
    parser.add_argument("--once", action="store_true", help="Capture snapshot once and print to stdout")
    args = parser.parse_args()

    agent = DeviceTelemetryAgent(
        server_url=args.server,
        region=args.region,
        device_type=args.device_type,
        device_name=args.name,
        department=args.department,
        interval=args.interval
    )

    if args.once:
        data = agent.collect()
        print(json.dumps(data, indent=2))
    else:
        agent.run_forever()


if __name__ == "__main__":
    main()
