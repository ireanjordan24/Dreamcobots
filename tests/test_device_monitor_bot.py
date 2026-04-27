"""
Tests for bots/device_monitor_bot/device_monitor_bot.py

Covers:
  1. ADBInterface simulated mode
  2. IOSInterface simulated mode
  3. BluetoothInterface simulated discovery
  4. WiFiInterface simulated scan and ping
  5. DeviceMonitorBot device listing
  6. DeviceMonitorBot Android snapshot
  7. DeviceMonitorBot iOS snapshot
  8. DeviceMonitorBot get_logs
  9. DeviceMonitorBot reboot_device
  10. DeviceMonitorBot install_apk
  11. DeviceMonitorBot dashboard
  12. DeviceMonitorBot get_capabilities
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.device_monitor_bot.device_monitor_bot import (
    ADBInterface,
    IOSInterface,
    BluetoothInterface,
    WiFiInterface,
    DeviceMonitorBot,
    DevicePlatform,
    MonitorStatus,
    ResourceSnapshot,
    DeviceInfo,
    BluetoothDevice,
    WifiNetwork,
)


# ---------------------------------------------------------------------------
# ADBInterface
# ---------------------------------------------------------------------------


class TestADBInterface:
    def test_list_devices_returns_list(self):
        adb = ADBInterface()
        devices = adb.list_devices()
        assert isinstance(devices, list)
        assert len(devices) >= 1

    def test_list_devices_have_required_fields(self):
        adb = ADBInterface()
        for device in adb.list_devices():
            assert isinstance(device, DeviceInfo)
            assert device.device_id
            assert device.platform == DevicePlatform.ANDROID

    def test_get_battery_returns_float(self):
        adb = ADBInterface()
        device_id = adb.list_devices()[0].device_id
        battery = adb.get_battery(device_id)
        assert isinstance(battery, float)
        assert 0.0 <= battery <= 100.0

    def test_get_cpu_percent_returns_float(self):
        adb = ADBInterface()
        device_id = adb.list_devices()[0].device_id
        cpu = adb.get_cpu_percent(device_id)
        assert isinstance(cpu, float)

    def test_get_memory_percent_returns_float(self):
        adb = ADBInterface()
        device_id = adb.list_devices()[0].device_id
        mem = adb.get_memory_percent(device_id)
        assert isinstance(mem, float)

    def test_logcat_returns_string(self):
        adb = ADBInterface()
        device_id = adb.list_devices()[0].device_id
        log = adb.logcat(device_id, lines=10)
        assert isinstance(log, str)
        assert len(log) > 0

    def test_install_apk_returns_dict(self):
        adb = ADBInterface()
        device_id = adb.list_devices()[0].device_id
        result = adb.install_apk(device_id, "/tmp/test.apk")
        assert "device_id" in result
        assert "success" in result

    def test_reboot_returns_dict(self):
        adb = ADBInterface()
        device_id = adb.list_devices()[0].device_id
        result = adb.reboot(device_id)
        assert result["device_id"] == device_id
        assert "action" in result


# ---------------------------------------------------------------------------
# IOSInterface
# ---------------------------------------------------------------------------


class TestIOSInterface:
    def test_list_devices_returns_list(self):
        ios = IOSInterface()
        devices = ios.list_devices()
        assert isinstance(devices, list)
        assert len(devices) >= 1

    def test_list_devices_platform(self):
        ios = IOSInterface()
        for device in ios.list_devices():
            assert device.platform == DevicePlatform.IOS

    def test_get_device_info_returns_dict(self):
        ios = IOSInterface()
        udid = ios.list_devices()[0].device_id
        info = ios.get_device_info(udid)
        assert isinstance(info, dict)
        assert len(info) > 0

    def test_get_syslog_returns_string(self):
        ios = IOSInterface()
        udid = ios.list_devices()[0].device_id
        log = ios.get_syslog(udid, lines=10)
        assert isinstance(log, str)

    def test_reboot_returns_dict(self):
        ios = IOSInterface()
        udid = ios.list_devices()[0].device_id
        result = ios.reboot(udid)
        assert "device_id" in result
        assert "action" in result


# ---------------------------------------------------------------------------
# BluetoothInterface
# ---------------------------------------------------------------------------


class TestBluetoothInterface:
    def test_scan_returns_list(self):
        bt = BluetoothInterface()
        devices = bt.scan()
        assert isinstance(devices, list)
        assert len(devices) >= 1

    def test_devices_are_bluetooth_device_instances(self):
        bt = BluetoothInterface()
        for d in bt.scan():
            assert isinstance(d, BluetoothDevice)
            assert d.address
            assert d.name

    def test_rssi_is_negative(self):
        bt = BluetoothInterface()
        for d in bt.scan():
            assert d.rssi < 0


# ---------------------------------------------------------------------------
# WiFiInterface
# ---------------------------------------------------------------------------


class TestWiFiInterface:
    def test_scan_returns_list(self):
        wifi = WiFiInterface()
        nets = wifi.scan()
        assert isinstance(nets, list)
        assert len(nets) >= 1

    def test_networks_are_wifi_network_instances(self):
        wifi = WiFiInterface()
        for n in wifi.scan():
            assert isinstance(n, WifiNetwork)
            assert n.ssid

    def test_ping_returns_dict(self):
        wifi = WiFiInterface()
        result = wifi.ping("8.8.8.8", count=1)
        assert "host" in result
        assert "status" in result


# ---------------------------------------------------------------------------
# DeviceMonitorBot
# ---------------------------------------------------------------------------


class TestDeviceMonitorBot:
    def setup_method(self):
        self.bot = DeviceMonitorBot()

    def test_list_devices_returns_dict(self):
        devices = self.bot.list_devices()
        assert isinstance(devices, dict)
        for platform_key in ("android", "ios", "bluetooth", "wifi"):
            assert platform_key in devices

    def test_list_devices_counts(self):
        devices = self.bot.list_devices()
        for v in devices.values():
            assert isinstance(v, list)
            assert len(v) >= 1

    def test_snapshot_android_returns_resource_snapshot(self):
        devices = self.bot.list_devices()["android"]
        snap = self.bot.snapshot_android(devices[0].device_id)
        assert isinstance(snap, ResourceSnapshot)
        assert snap.device_id == devices[0].device_id
        assert 0.0 <= snap.battery_percent <= 100.0

    def test_snapshot_android_stored_in_history(self):
        devices = self.bot.list_devices()["android"]
        before = len(self.bot._snapshots)
        self.bot.snapshot_android(devices[0].device_id)
        assert len(self.bot._snapshots) == before + 1

    def test_snapshot_ios_returns_resource_snapshot(self):
        devices = self.bot.list_devices()["ios"]
        snap = self.bot.snapshot_ios(devices[0].device_id)
        assert isinstance(snap, ResourceSnapshot)

    def test_get_logs_android(self):
        devices = self.bot.list_devices()["android"]
        result = self.bot.get_logs(devices[0].device_id, DevicePlatform.ANDROID, lines=5)
        assert "log" in result
        assert result["platform"] == "android"

    def test_get_logs_ios(self):
        devices = self.bot.list_devices()["ios"]
        result = self.bot.get_logs(devices[0].device_id, DevicePlatform.IOS, lines=5)
        assert "log" in result
        assert result["platform"] == "ios"

    def test_reboot_device_android(self):
        devices = self.bot.list_devices()["android"]
        result = self.bot.reboot_device(devices[0].device_id, DevicePlatform.ANDROID)
        assert "device_id" in result

    def test_reboot_device_unsupported_platform(self):
        result = self.bot.reboot_device("somedevice", DevicePlatform.BLUETOOTH)
        assert result["status"] == "unsupported"

    def test_install_apk(self):
        devices = self.bot.list_devices()["android"]
        result = self.bot.install_apk(devices[0].device_id, "/tmp/app.apk")
        assert "success" in result

    def test_ping(self):
        result = self.bot.ping("8.8.8.8")
        assert "host" in result

    def test_scan_wifi(self):
        nets = self.bot.scan_wifi()
        assert isinstance(nets, list)

    def test_dashboard_keys(self):
        dash = self.bot.dashboard()
        for key in ("session_id", "total_devices_discovered", "devices_by_platform", "status"):
            assert key in dash

    def test_get_capabilities_keys(self):
        caps = self.bot.get_capabilities()
        assert caps["bot_id"] == "device_monitor_bot"
        assert "features" in caps
        assert len(caps["features"]) > 0

    def test_disabled_adb_raises(self):
        bot = DeviceMonitorBot(enable_adb=False)
        with pytest.raises(RuntimeError, match="ADB"):
            bot.snapshot_android("any-device")

    def test_disabled_ios_raises(self):
        bot = DeviceMonitorBot(enable_ios=False)
        with pytest.raises(RuntimeError, match="iOS"):
            bot.snapshot_ios("any-udid")

    def test_disabled_wifi_raises(self):
        bot = DeviceMonitorBot(enable_wifi=False)
        with pytest.raises(RuntimeError, match="WiFi"):
            bot.ping("8.8.8.8")
