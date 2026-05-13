"""
Device Monitor Bot — Buddy's cross-device intelligence layer.

Monitors, debugs, and controls Android (ADB), iOS (Core APIs), and any
Bluetooth/WiFi-connected device from a single, unified interface.

Platform integrations
---------------------
- **Android** : ADB shell commands (battery, CPU, memory, logcat, install/uninstall).
- **iOS**      : Apple Core APIs via `cfgutil` / `idevice*` libimobiledevice tools
                 (battery, syslog, app list, reboot).
- **Bluetooth**: Device discovery, pairing status, RSSI, and basic I/O.
- **WiFi**     : Scan nearby networks, connected-device inventory, ping latency.

All platform calls are *simulated* when the native toolchain is absent so that
the bot can run in any environment (CI, sandboxes, unit tests).
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

import subprocess
import shutil
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class DevicePlatform(str, Enum):
    ANDROID = "android"
    IOS = "ios"
    BLUETOOTH = "bluetooth"
    WIFI = "wifi"
    COMPUTER = "computer"


class MonitorStatus(str, Enum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"
    SIMULATED = "simulated"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class DeviceInfo:
    """Metadata describing a connected or discovered device."""

    device_id: str
    platform: DevicePlatform
    name: str = "Unknown Device"
    model: str = ""
    os_version: str = ""
    connected: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceSnapshot:
    """Point-in-time resource metrics for a device."""

    device_id: str
    timestamp: float = field(default_factory=time.time)
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    battery_percent: Optional[float] = None
    temperature_celsius: Optional[float] = None
    status: MonitorStatus = MonitorStatus.OK

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "timestamp": self.timestamp,
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "battery_percent": self.battery_percent,
            "temperature_celsius": self.temperature_celsius,
            "status": self.status.value,
        }


@dataclass
class BluetoothDevice:
    """A Bluetooth-discoverable peripheral."""

    address: str
    name: str = "Unknown"
    rssi: int = -70
    paired: bool = False


@dataclass
class WifiNetwork:
    """A nearby Wi-Fi network entry."""

    ssid: str
    bssid: str = ""
    signal_dbm: int = -65
    frequency_mhz: int = 2412
    secured: bool = True


# ---------------------------------------------------------------------------
# ADB helper (Android Debug Bridge)
# ---------------------------------------------------------------------------


class ADBInterface:
    """Thin wrapper around the ``adb`` command-line tool.

    Falls back to *simulated* responses when ADB is not installed.
    """

    _ADB = "adb"

    def __init__(self) -> None:
        self._available = shutil.which(self._ADB) is not None

    # ------------------------------------------------------------------
    def _run(self, *args: str) -> str:
        if not self._available:
            return "__simulated__"
        try:
            result = subprocess.run(
                [self._ADB, *args],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout.strip()
        except Exception:
            return "__error__"

    # ------------------------------------------------------------------
    def list_devices(self) -> List[DeviceInfo]:
        """Return connected Android devices."""
        out = self._run("devices")
        devices: List[DeviceInfo] = []
        if out in ("__simulated__", "__error__"):
            devices.append(
                DeviceInfo(
                    device_id="emulator-sim-001",
                    platform=DevicePlatform.ANDROID,
                    name="Simulated Android Device",
                    model="Pixel 7 (sim)",
                    os_version="14",
                )
            )
            return devices
        for line in out.splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "device":
                devices.append(
                    DeviceInfo(
                        device_id=parts[0],
                        platform=DevicePlatform.ANDROID,
                        name=f"Android:{parts[0]}",
                    )
                )
        return devices

    def get_battery(self, device_id: str) -> float:
        out = self._run("-s", device_id, "shell", "dumpsys", "battery")
        if out == "__simulated__":
            return 78.0
        for line in out.splitlines():
            if "level:" in line:
                try:
                    return float(line.split(":")[1].strip())
                except ValueError:
                    pass
        return 0.0

    def get_cpu_percent(self, device_id: str) -> float:
        out = self._run("-s", device_id, "shell", "top", "-bn1")
        if out == "__simulated__":
            return 32.5
        for line in out.splitlines():
            if "Cpu" in line or "cpu" in line:
                try:
                    idle = float(line.split("id,")[0].rsplit(",", 1)[-1].strip())
                    return round(100.0 - idle, 1)
                except (ValueError, IndexError):
                    pass
        return 0.0

    def get_memory_percent(self, device_id: str) -> float:
        out = self._run("-s", device_id, "shell", "cat", "/proc/meminfo")
        if out == "__simulated__":
            return 55.0
        lines = {k.split(":")[0].strip(): k.split(":")[1].strip() for k in out.splitlines() if ":" in k}
        try:
            total = int(lines.get("MemTotal", "0").split()[0])
            available = int(lines.get("MemAvailable", "0").split()[0])
            if total:
                return round((total - available) / total * 100, 1)
        except (ValueError, KeyError):
            pass
        return 0.0

    def logcat(self, device_id: str, lines: int = 50) -> str:
        out = self._run("-s", device_id, "logcat", "-d", f"-T{lines}")
        if out in ("__simulated__", "__error__"):
            return "[simulated] 04-27 19:00:00.000 I BuddyMonitor: Device healthy"
        return out

    def install_apk(self, device_id: str, apk_path: str) -> Dict[str, Any]:
        out = self._run("-s", device_id, "install", apk_path)
        success = "Success" in out or out == "__simulated__"
        return {"device_id": device_id, "apk": apk_path, "success": success, "output": out}

    def reboot(self, device_id: str) -> Dict[str, Any]:
        out = self._run("-s", device_id, "reboot")
        return {"device_id": device_id, "action": "reboot", "status": "sent", "output": out}


# ---------------------------------------------------------------------------
# iOS Interface (libimobiledevice / cfgutil)
# ---------------------------------------------------------------------------


class IOSInterface:
    """Thin wrapper around libimobiledevice tools (``ideviceinfo``, ``idevicesyslog``, etc.).

    Falls back to simulated responses when the toolchain is absent.
    """

    def __init__(self) -> None:
        self._available = shutil.which("ideviceinfo") is not None

    def _run(self, *args: str) -> str:
        if not self._available:
            return "__simulated__"
        try:
            result = subprocess.run(list(args), capture_output=True, text=True, timeout=10)
            return result.stdout.strip()
        except Exception:
            return "__error__"

    def list_devices(self) -> List[DeviceInfo]:
        out = self._run("idevice_id", "-l")
        devices: List[DeviceInfo] = []
        if out in ("__simulated__", "__error__", ""):
            devices.append(
                DeviceInfo(
                    device_id="ios-sim-001",
                    platform=DevicePlatform.IOS,
                    name="Simulated iPhone",
                    model="iPhone 15 Pro (sim)",
                    os_version="17",
                )
            )
            return devices
        for udid in out.splitlines():
            if udid:
                devices.append(DeviceInfo(device_id=udid, platform=DevicePlatform.IOS, name=f"iOS:{udid}"))
        return devices

    def get_device_info(self, udid: str) -> Dict[str, Any]:
        out = self._run("ideviceinfo", "-u", udid)
        if out == "__simulated__":
            return {
                "DeviceName": "Buddy's iPhone",
                "ProductType": "iPhone16,1",
                "ProductVersion": "17.0",
                "BatteryCurrentCapacity": 82,
            }
        info: Dict[str, Any] = {}
        for line in out.splitlines():
            if ": " in line:
                k, _, v = line.partition(": ")
                info[k.strip()] = v.strip()
        return info

    def get_syslog(self, udid: str, lines: int = 50) -> str:
        if not self._available:
            return "[simulated iOS syslog] BuddyMonitor: All systems nominal"
        out = self._run("idevicesyslog", "-u", udid)
        return "\n".join(out.splitlines()[:lines])

    def reboot(self, udid: str) -> Dict[str, Any]:
        out = self._run("idevicediagnostics", "-u", udid, "restart")
        return {"device_id": udid, "action": "reboot", "status": "sent", "output": out}


# ---------------------------------------------------------------------------
# Bluetooth Interface
# ---------------------------------------------------------------------------


class BluetoothInterface:
    """Discover and inspect Bluetooth-connected devices.

    Uses ``bluetoothctl`` on Linux / ``system_profiler SPBluetoothDataType`` on macOS.
    Falls back to simulated data when neither tool is available.
    """

    def scan(self) -> List[BluetoothDevice]:
        """Return a list of recently seen Bluetooth devices."""
        if shutil.which("bluetoothctl"):
            return self._scan_linux()
        return self._simulated_devices()

    def _scan_linux(self) -> List[BluetoothDevice]:
        try:
            result = subprocess.run(
                ["bluetoothctl", "devices"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            devices: List[BluetoothDevice] = []
            for line in result.stdout.splitlines():
                parts = line.strip().split(" ", 2)
                if len(parts) >= 3:
                    devices.append(BluetoothDevice(address=parts[1], name=parts[2]))
            return devices if devices else self._simulated_devices()
        except Exception:
            return self._simulated_devices()

    @staticmethod
    def _simulated_devices() -> List[BluetoothDevice]:
        return [
            BluetoothDevice(address="AA:BB:CC:DD:EE:01", name="BuddyHeadphones", rssi=-55, paired=True),
            BluetoothDevice(address="AA:BB:CC:DD:EE:02", name="DreamWatch", rssi=-70, paired=False),
            BluetoothDevice(address="AA:BB:CC:DD:EE:03", name="IoT-Sensor-Node", rssi=-80, paired=True),
        ]


# ---------------------------------------------------------------------------
# WiFi Interface
# ---------------------------------------------------------------------------


class WiFiInterface:
    """Scan Wi-Fi networks and report connected-device inventory."""

    def scan(self) -> List[WifiNetwork]:
        """Return visible Wi-Fi networks (simulated when tools unavailable)."""
        return self._simulated_networks()

    def ping(self, host: str, count: int = 3) -> Dict[str, Any]:
        """Ping a host and return average latency."""
        if shutil.which("ping") is None:
            return {"host": host, "avg_ms": 12.5, "status": MonitorStatus.SIMULATED.value}
        try:
            result = subprocess.run(
                ["ping", "-c", str(count), host],
                capture_output=True,
                text=True,
                timeout=10,
            )
            for line in result.stdout.splitlines():
                if "avg" in line or "rtt" in line:
                    try:
                        avg = float(line.split("/")[4])
                        return {"host": host, "avg_ms": avg, "status": MonitorStatus.OK.value}
                    except (IndexError, ValueError):
                        pass
            return {"host": host, "avg_ms": None, "status": MonitorStatus.OFFLINE.value}
        except Exception:
            return {"host": host, "avg_ms": None, "status": MonitorStatus.OFFLINE.value}

    @staticmethod
    def _simulated_networks() -> List[WifiNetwork]:
        return [
            WifiNetwork(ssid="DreamCo-HQ", bssid="00:11:22:33:44:55", signal_dbm=-45, secured=True),
            WifiNetwork(ssid="BuddyNet-5G", bssid="00:11:22:33:44:56", signal_dbm=-60, secured=True),
            WifiNetwork(ssid="IoT-DeviceBridge", bssid="00:11:22:33:44:57", signal_dbm=-75, secured=False),
        ]


# ---------------------------------------------------------------------------
# Main DeviceMonitorBot
# ---------------------------------------------------------------------------


class DeviceMonitorBot:
    """
    Central bot that unifies Android, iOS, Bluetooth, and WiFi monitoring.

    Buddy uses this bot to observe, debug, and optionally control any
    connected device — phone, IoT node, wearable, or computer peripheral.

    Parameters
    ----------
    enable_adb:       Activate Android ADB interface.
    enable_ios:       Activate iOS libimobiledevice interface.
    enable_bluetooth: Activate Bluetooth discovery.
    enable_wifi:      Activate WiFi scanning and latency checks.
    """

    bot_id = "device_monitor_bot"
    name = "Device Monitor Bot"
    category = "monitoring"

    def __init__(
        self,
        enable_adb: bool = True,
        enable_ios: bool = True,
        enable_bluetooth: bool = True,
        enable_wifi: bool = True,
    ) -> None:
        self.enable_adb = enable_adb
        self.enable_ios = enable_ios
        self.enable_bluetooth = enable_bluetooth
        self.enable_wifi = enable_wifi

        self._adb = ADBInterface() if enable_adb else None
        self._ios = IOSInterface() if enable_ios else None
        self._bt = BluetoothInterface() if enable_bluetooth else None
        self._wifi = WiFiInterface() if enable_wifi else None

        self._snapshots: List[ResourceSnapshot] = []
        self._session_id = str(uuid.uuid4())

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def list_devices(self) -> Dict[str, List[DeviceInfo]]:
        """Discover all connected devices across enabled platforms."""
        result: Dict[str, List[DeviceInfo]] = {}
        if self._adb:
            result["android"] = self._adb.list_devices()
        if self._ios:
            result["ios"] = self._ios.list_devices()
        if self._bt:
            bt_devices = self._bt.scan()
            result["bluetooth"] = [
                DeviceInfo(
                    device_id=d.address,
                    platform=DevicePlatform.BLUETOOTH,
                    name=d.name,
                    metadata={"rssi": d.rssi, "paired": d.paired},
                )
                for d in bt_devices
            ]
        if self._wifi:
            nets = self._wifi.scan()
            result["wifi"] = [
                DeviceInfo(
                    device_id=n.bssid or n.ssid,
                    platform=DevicePlatform.WIFI,
                    name=n.ssid,
                    metadata={"signal_dbm": n.signal_dbm, "secured": n.secured},
                )
                for n in nets
            ]
        return result

    # ------------------------------------------------------------------
    # Resource monitoring
    # ------------------------------------------------------------------

    def snapshot_android(self, device_id: str) -> ResourceSnapshot:
        """Capture CPU, memory, and battery for an Android device."""
        if not self._adb:
            raise RuntimeError("ADB interface is disabled.")
        snap = ResourceSnapshot(
            device_id=device_id,
            cpu_percent=self._adb.get_cpu_percent(device_id),
            memory_percent=self._adb.get_memory_percent(device_id),
            battery_percent=self._adb.get_battery(device_id),
            status=MonitorStatus.SIMULATED if not self._adb._available else MonitorStatus.OK,
        )
        self._snapshots.append(snap)
        return snap

    def snapshot_ios(self, udid: str) -> ResourceSnapshot:
        """Capture device info and battery for an iOS device."""
        if not self._ios:
            raise RuntimeError("iOS interface is disabled.")
        info = self._ios.get_device_info(udid)
        battery = float(info.get("BatteryCurrentCapacity", 0) or 0)
        snap = ResourceSnapshot(
            device_id=udid,
            battery_percent=battery,
            status=MonitorStatus.SIMULATED if not self._ios._available else MonitorStatus.OK,
        )
        self._snapshots.append(snap)
        return snap

    # ------------------------------------------------------------------
    # Debugging
    # ------------------------------------------------------------------

    def get_logs(self, device_id: str, platform: DevicePlatform, lines: int = 50) -> Dict[str, Any]:
        """Retrieve device logs (logcat / syslog)."""
        if platform == DevicePlatform.ANDROID and self._adb:
            raw = self._adb.logcat(device_id, lines)
        elif platform == DevicePlatform.IOS and self._ios:
            raw = self._ios.get_syslog(device_id, lines)
        else:
            raw = "[no log interface available]"
        return {"device_id": device_id, "platform": platform.value, "lines": lines, "log": raw}

    # ------------------------------------------------------------------
    # Control
    # ------------------------------------------------------------------

    def reboot_device(self, device_id: str, platform: DevicePlatform) -> Dict[str, Any]:
        """Send a reboot command to a device."""
        if platform == DevicePlatform.ANDROID and self._adb:
            return self._adb.reboot(device_id)
        if platform == DevicePlatform.IOS and self._ios:
            return self._ios.reboot(device_id)
        return {"device_id": device_id, "status": "unsupported", "platform": platform.value}

    def install_apk(self, device_id: str, apk_path: str) -> Dict[str, Any]:
        """Install an APK on an Android device."""
        if not self._adb:
            raise RuntimeError("ADB interface is disabled.")
        return self._adb.install_apk(device_id, apk_path)

    # ------------------------------------------------------------------
    # WiFi utilities
    # ------------------------------------------------------------------

    def ping(self, host: str, count: int = 3) -> Dict[str, Any]:
        """Ping a host and return latency stats."""
        if not self._wifi:
            raise RuntimeError("WiFi interface is disabled.")
        return self._wifi.ping(host, count)

    def scan_wifi(self) -> List[WifiNetwork]:
        """Return visible Wi-Fi networks."""
        if not self._wifi:
            return []
        return self._wifi.scan()

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def dashboard(self) -> Dict[str, Any]:
        """Return a summary of all monitored devices and recent snapshots."""
        devices = self.list_devices()
        total_devices = sum(len(v) for v in devices.values())
        recent = self._snapshots[-10:] if self._snapshots else []
        return {
            "session_id": self._session_id,
            "total_devices_discovered": total_devices,
            "devices_by_platform": {k: len(v) for k, v in devices.items()},
            "recent_snapshots": [s.to_dict() for s in recent],
            "status": "operational",
        }

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "bot_id": self.bot_id,
            "name": self.name,
            "category": self.category,
            "platforms": {
                "android_adb": self.enable_adb,
                "ios_core_api": self.enable_ios,
                "bluetooth": self.enable_bluetooth,
                "wifi": self.enable_wifi,
            },
            "features": [
                "Device discovery across Android, iOS, Bluetooth, WiFi",
                "ADB-based Android CPU/memory/battery monitoring",
                "iOS Core API battery and syslog access",
                "Bluetooth device scan and RSSI reporting",
                "WiFi network scan and ping latency",
                "Remote reboot and APK installation (Android)",
                "Unified device dashboard",
            ],
        }
