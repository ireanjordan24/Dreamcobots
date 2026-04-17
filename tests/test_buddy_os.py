"""
Tests for bots/buddy_os/

Covers:
  1. Tiers
  2. Device Manager
  3. Bluetooth Engine
  4. Cast Engine
  5. App Framework (AppRegistry, BrowserToolkit, SmartDeviceHub,
                    NvidiaToolsHub, StarlinkManager)
  6. BuddyOS main class (integration + chat)
"""

import os
import sys

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.buddy_os.app_framework import (
    NVIDIA_MARKUP_PCT,
    NVIDIA_TOOLS,
    STARLINK_MARKUP_PCT,
    STARLINK_PLANS,
    AppCategory,
    AppPlatform,
    AppRegistry,
    BrowserToolkit,
    NvidiaToolsHub,
    SmartDeviceHub,
    SmartDeviceProtocol,
    StarlinkManager,
)
from bots.buddy_os.bluetooth_engine import (
    BluetoothDevice,
    BluetoothEngine,
    BluetoothProfileType,
    BluetoothState,
    FileTransfer,
)
from bots.buddy_os.buddy_os import BuddyOS, BuddyOSError, BuddyOSTierError
from bots.buddy_os.cast_engine import (
    CastEngine,
    CastProtocol,
    CastReceiver,
    CastSession,
    CastState,
    ContentType,
)
from bots.buddy_os.device_manager import (
    DEVICE_COMPATIBILITY_MATRIX,
    Device,
    DeviceManager,
    DevicePlatform,
    DeviceStatus,
    DeviceType,
)

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
from bots.buddy_os.tiers import (
    FEATURE_APP_FRAMEWORK,
    FEATURE_BLUETOOTH,
    FEATURE_CAST_SCREEN,
    FEATURE_DEVICE_MANAGER,
    FEATURE_MULTI_CAST,
    FEATURE_NVIDIA_TOOLS,
    FEATURE_STARLINK,
    FEATURE_WHITE_LABEL,
    TIER_CATALOGUE,
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
)

# ===========================================================================
# 1. Tiers
# ===========================================================================


class TestTiers:
    def test_three_tiers_exist(self):
        assert len(list_tiers()) == 3

    def test_free_tier_price(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_pro_tier_price(self):
        assert get_tier_config(Tier.PRO).price_usd_monthly == 49.0

    def test_enterprise_tier_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 199.0

    def test_enterprise_unlimited_devices(self):
        assert get_tier_config(Tier.ENTERPRISE).is_unlimited_devices()

    def test_free_limited_devices(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_paired_devices is not None
        assert cfg.max_paired_devices > 0

    def test_upgrade_path_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_no_upgrade_from_enterprise(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_free_has_bluetooth(self):
        assert FEATURE_BLUETOOTH in get_tier_config(Tier.FREE).features

    def test_enterprise_has_white_label(self):
        assert FEATURE_WHITE_LABEL in get_tier_config(Tier.ENTERPRISE).features

    def test_pro_has_multi_cast(self):
        assert FEATURE_MULTI_CAST in get_tier_config(Tier.PRO).features

    def test_has_feature_method(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_DEVICE_MANAGER)
        assert not cfg.has_feature(FEATURE_WHITE_LABEL)


# ===========================================================================
# 2. Device Manager
# ===========================================================================


class TestDeviceManager:
    def test_register_phone(self):
        dm = DeviceManager()
        device = dm.register_device("My Phone", DeviceType.PHONE, DevicePlatform.APPLE)
        assert device.device_id.startswith("dev_")
        assert device.name == "My Phone"

    def test_register_tv(self):
        dm = DeviceManager()
        device = dm.register_device(
            "Living Room TV", DeviceType.TV, DevicePlatform.SAMSUNG
        )
        assert device.device_type == DeviceType.TV

    def test_connect_device(self):
        dm = DeviceManager()
        dev = dm.register_device("Tablet", DeviceType.TABLET, DevicePlatform.GOOGLE)
        dm.connect(dev.device_id)
        assert dm.get_device(dev.device_id).status == DeviceStatus.CONNECTED

    def test_disconnect_device(self):
        dm = DeviceManager()
        dev = dm.register_device("PC", DeviceType.COMPUTER, DevicePlatform.WINDOWS)
        dm.connect(dev.device_id)
        dm.disconnect(dev.device_id)
        assert dm.get_device(dev.device_id).status == DeviceStatus.DISCONNECTED

    def test_get_connected_devices(self):
        dm = DeviceManager()
        dev1 = dm.register_device("Phone", DeviceType.PHONE, DevicePlatform.APPLE)
        dev2 = dm.register_device("Tablet", DeviceType.TABLET, DevicePlatform.GOOGLE)
        dm.connect(dev1.device_id)
        connected = dm.get_connected_devices()
        assert len(connected) == 1

    def test_list_devices_by_type(self):
        dm = DeviceManager()
        dm.register_device("Phone1", DeviceType.PHONE, DevicePlatform.APPLE)
        dm.register_device("TV1", DeviceType.TV, DevicePlatform.SAMSUNG)
        phones = dm.list_devices(device_type=DeviceType.PHONE)
        assert len(phones) == 1

    def test_list_devices_by_platform(self):
        dm = DeviceManager()
        dm.register_device("iPhone", DeviceType.PHONE, DevicePlatform.APPLE)
        dm.register_device("iPad", DeviceType.TABLET, DevicePlatform.APPLE)
        dm.register_device("Android", DeviceType.PHONE, DevicePlatform.GOOGLE)
        apple_devices = dm.list_devices(platform=DevicePlatform.APPLE)
        assert len(apple_devices) == 2

    def test_remove_device(self):
        dm = DeviceManager()
        dev = dm.register_device("Phone", DeviceType.PHONE, DevicePlatform.APPLE)
        dm.remove_device(dev.device_id)
        assert len(dm.list_devices()) == 0

    def test_device_limit(self):
        dm = DeviceManager(max_devices=2)
        dm.register_device("D1", DeviceType.PHONE, DevicePlatform.APPLE)
        dm.register_device("D2", DeviceType.TABLET, DevicePlatform.GOOGLE)
        with pytest.raises(RuntimeError, match="limit"):
            dm.register_device("D3", DeviceType.COMPUTER, DevicePlatform.WINDOWS)

    def test_incompatible_platform_raises(self):
        dm = DeviceManager()
        # COMPUTER only supports Apple/Windows/Linux; Samsung is not supported
        with pytest.raises(ValueError):
            dm.register_device(
                "Samsung PC", DeviceType.COMPUTER, DevicePlatform.SAMSUNG
            )

    def test_compatibility_matrix_returned(self):
        dm = DeviceManager()
        matrix = dm.get_compatibility_matrix()
        assert "phone" in matrix
        assert "apple" in matrix["phone"]

    def test_device_not_found_raises(self):
        dm = DeviceManager()
        with pytest.raises(KeyError):
            dm.get_device("dev_9999")

    def test_device_to_dict(self):
        dm = DeviceManager()
        dev = dm.register_device("Mac", DeviceType.COMPUTER, DevicePlatform.APPLE)
        d = dev.to_dict()
        assert d["name"] == "Mac"
        assert d["type"] == DeviceType.COMPUTER.value


# ===========================================================================
# 3. Bluetooth Engine
# ===========================================================================


class TestBluetoothEngine:
    def test_start_scan(self):
        bt = BluetoothEngine()
        result = bt.start_scan()
        assert result["scanning"] is True

    def test_stop_scan(self):
        bt = BluetoothEngine()
        bt.start_scan()
        result = bt.stop_scan()
        assert result["scanning"] is False

    def test_add_discovered_device(self):
        bt = BluetoothEngine()
        dev = bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "JBL Speaker")
        assert dev.name == "JBL Speaker"

    def test_pair_device(self):
        bt = BluetoothEngine()
        bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "Speaker")
        paired = bt.pair_device("AA:BB:CC:DD:EE:FF")
        assert paired.paired is True
        assert paired.state == BluetoothState.PAIRED

    def test_connect_device(self):
        bt = BluetoothEngine()
        bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "Speaker")
        bt.pair_device("AA:BB:CC:DD:EE:FF")
        connected = bt.connect("AA:BB:CC:DD:EE:FF")
        assert connected.state == BluetoothState.CONNECTED

    def test_disconnect_device(self):
        bt = BluetoothEngine()
        bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "Speaker")
        bt.pair_device("AA:BB:CC:DD:EE:FF")
        bt.connect("AA:BB:CC:DD:EE:FF")
        bt.disconnect("AA:BB:CC:DD:EE:FF")
        dev = bt._paired["AA:BB:CC:DD:EE:FF"]
        assert dev.state == BluetoothState.PAIRED

    def test_trust_device(self):
        bt = BluetoothEngine()
        bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "Speaker")
        bt.pair_device("AA:BB:CC:DD:EE:FF")
        bt.trust_device("AA:BB:CC:DD:EE:FF")
        assert bt._paired["AA:BB:CC:DD:EE:FF"].trusted is True

    def test_unpair_device(self):
        bt = BluetoothEngine()
        bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "Speaker")
        bt.pair_device("AA:BB:CC:DD:EE:FF")
        bt.unpair_device("AA:BB:CC:DD:EE:FF")
        assert "AA:BB:CC:DD:EE:FF" not in bt._paired

    def test_pairing_limit(self):
        bt = BluetoothEngine(max_paired=1)
        bt.add_discovered_device("AA:BB:CC:DD:EE:01", "Dev1")
        bt.add_discovered_device("AA:BB:CC:DD:EE:02", "Dev2")
        bt.pair_device("AA:BB:CC:DD:EE:01")
        with pytest.raises(RuntimeError, match="limit"):
            bt.pair_device("AA:BB:CC:DD:EE:02")

    def test_pair_unknown_raises(self):
        bt = BluetoothEngine()
        with pytest.raises(KeyError):
            bt.pair_device("FF:FF:FF:FF:FF:FF")

    def test_connect_unpaired_raises(self):
        bt = BluetoothEngine()
        with pytest.raises(KeyError):
            bt.connect("FF:FF:FF:FF:FF:FF")

    def test_file_transfer(self):
        bt = BluetoothEngine()
        bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "Phone")
        bt.pair_device("AA:BB:CC:DD:EE:FF")
        bt.connect("AA:BB:CC:DD:EE:FF")
        transfer = bt.send_file("AA:BB:CC:DD:EE:FF", "photo.jpg", 1024)
        assert transfer.filename == "photo.jpg"
        assert transfer.status == "in_progress"

    def test_file_transfer_requires_connection(self):
        bt = BluetoothEngine()
        bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "Phone")
        bt.pair_device("AA:BB:CC:DD:EE:FF")
        with pytest.raises(RuntimeError, match="not connected"):
            bt.send_file("AA:BB:CC:DD:EE:FF", "file.txt", 100)

    def test_transfer_progress(self):
        bt = BluetoothEngine()
        bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "Phone")
        bt.pair_device("AA:BB:CC:DD:EE:FF")
        bt.connect("AA:BB:CC:DD:EE:FF")
        transfer = bt.send_file("AA:BB:CC:DD:EE:FF", "video.mp4", 2000)
        bt.update_transfer_progress(transfer.transfer_id, 2000)
        updated = bt.get_transfer(transfer.transfer_id)
        assert updated.status == "completed"
        assert updated.progress_pct == 100.0

    def test_get_connected_bluetooth_devices(self):
        bt = BluetoothEngine()
        bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "Phone")
        bt.pair_device("AA:BB:CC:DD:EE:FF")
        bt.connect("AA:BB:CC:DD:EE:FF")
        assert len(bt.get_connected_devices()) == 1

    def test_bluetooth_device_to_dict(self):
        bt = BluetoothEngine()
        dev = bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "Speaker")
        d = dev.to_dict()
        assert d["name"] == "Speaker"
        assert d["address"] == "AA:BB:CC:DD:EE:FF"


# ===========================================================================
# 4. Cast Engine
# ===========================================================================


class TestCastEngine:
    def test_add_google_cast_receiver(self):
        cast = CastEngine()
        recv = cast.add_receiver(
            "Living Room TV", CastProtocol.GOOGLE_CAST, ip_address="192.168.1.5"
        )
        assert recv.protocol == CastProtocol.GOOGLE_CAST

    def test_add_airplay_receiver(self):
        cast = CastEngine()
        recv = cast.add_receiver("Apple TV", CastProtocol.AIRPLAY)
        assert recv.name == "Apple TV"

    def test_start_cast_session(self):
        cast = CastEngine()
        recv = cast.add_receiver("TV", CastProtocol.MIRACAST)
        session = cast.start_cast(
            recv.receiver_id, ContentType.VIDEO, "https://example.com/v.mp4"
        )
        assert session.state == CastState.CASTING

    def test_pause_and_resume(self):
        cast = CastEngine()
        recv = cast.add_receiver("TV", CastProtocol.GOOGLE_CAST)
        session = cast.start_cast(
            recv.receiver_id, ContentType.VIDEO, "https://example.com/v.mp4"
        )
        cast.pause_cast(session.session_id)
        assert cast.get_session(session.session_id).state == CastState.PAUSED
        cast.resume_cast(session.session_id)
        assert cast.get_session(session.session_id).state == CastState.CASTING

    def test_stop_cast(self):
        cast = CastEngine()
        recv = cast.add_receiver("TV", CastProtocol.HDMI)
        session = cast.start_cast(recv.receiver_id, ContentType.SCREEN_MIRROR, "")
        cast.stop_cast(session.session_id)
        assert cast.get_session(session.session_id).state == CastState.STOPPED

    def test_seek(self):
        cast = CastEngine()
        recv = cast.add_receiver("TV", CastProtocol.GOOGLE_CAST)
        session = cast.start_cast(
            recv.receiver_id, ContentType.VIDEO, "url", duration_seconds=3600
        )
        cast.seek(session.session_id, 120.0)
        assert cast.get_session(session.session_id).position_seconds == 120.0

    def test_seek_clamped(self):
        cast = CastEngine()
        recv = cast.add_receiver("TV", CastProtocol.GOOGLE_CAST)
        session = cast.start_cast(
            recv.receiver_id, ContentType.VIDEO, "url", duration_seconds=60
        )
        cast.seek(session.session_id, 9999)
        assert cast.get_session(session.session_id).position_seconds == 60.0

    def test_set_volume(self):
        cast = CastEngine()
        recv = cast.add_receiver("TV", CastProtocol.AIRPLAY)
        cast.set_volume(recv.receiver_id, 0.8)
        assert cast._receivers[recv.receiver_id].volume == 0.8

    def test_volume_clamped(self):
        cast = CastEngine()
        recv = cast.add_receiver("TV", CastProtocol.AIRPLAY)
        cast.set_volume(recv.receiver_id, 5.0)
        assert cast._receivers[recv.receiver_id].volume == 1.0

    def test_cast_target_limit(self):
        cast = CastEngine(max_targets=1)
        cast.add_receiver("TV1", CastProtocol.GOOGLE_CAST)
        with pytest.raises(RuntimeError, match="limit"):
            cast.add_receiver("TV2", CastProtocol.AIRPLAY)

    def test_list_receivers_by_protocol(self):
        cast = CastEngine()
        cast.add_receiver("TV1", CastProtocol.GOOGLE_CAST)
        cast.add_receiver("TV2", CastProtocol.AIRPLAY)
        cast.add_receiver("TV3", CastProtocol.GOOGLE_CAST)
        google_recvs = cast.list_receivers(protocol=CastProtocol.GOOGLE_CAST)
        assert len(google_recvs) == 2

    def test_list_active_sessions(self):
        cast = CastEngine()
        recv = cast.add_receiver("TV", CastProtocol.GOOGLE_CAST)
        sess = cast.start_cast(recv.receiver_id, ContentType.VIDEO, "url")
        cast.stop_cast(sess.session_id)
        recv2 = cast.add_receiver("TV2", CastProtocol.AIRPLAY)
        cast.start_cast(recv2.receiver_id, ContentType.AUDIO, "audio_url")
        active = cast.list_sessions(active_only=True)
        assert len(active) == 1

    def test_receiver_not_found_raises(self):
        cast = CastEngine()
        with pytest.raises(KeyError):
            cast.start_cast("recv_9999", ContentType.VIDEO, "url")

    def test_session_to_dict(self):
        cast = CastEngine()
        recv = cast.add_receiver("TV", CastProtocol.GOOGLE_CAST)
        session = cast.start_cast(
            recv.receiver_id, ContentType.VIDEO, "https://example.com"
        )
        d = session.to_dict()
        assert d["content_type"] == ContentType.VIDEO.value


# ===========================================================================
# 5. App Framework
# ===========================================================================


class TestAppRegistry:
    def test_install_app(self):
        reg = AppRegistry()
        app = reg.install("Netflix", AppCategory.ENTERTAINMENT, [AppPlatform.UNIVERSAL])
        assert app.name == "Netflix"
        assert app.enabled is True

    def test_disable_app(self):
        reg = AppRegistry()
        app = reg.install("Slack", AppCategory.COMMUNICATION, [AppPlatform.DESKTOP])
        reg.disable(app.app_id)
        assert reg.get_app(app.app_id).enabled is False

    def test_enable_app(self):
        reg = AppRegistry()
        app = reg.install("Slack", AppCategory.COMMUNICATION, [AppPlatform.DESKTOP])
        reg.disable(app.app_id)
        reg.enable(app.app_id)
        assert reg.get_app(app.app_id).enabled is True

    def test_uninstall_app(self):
        reg = AppRegistry()
        app = reg.install("App", AppCategory.UTILITIES, [AppPlatform.MOBILE])
        reg.uninstall(app.app_id)
        assert len(reg.list_apps()) == 0

    def test_list_apps_by_category(self):
        reg = AppRegistry()
        reg.install("YouTube", AppCategory.ENTERTAINMENT, [AppPlatform.UNIVERSAL])
        reg.install("Slack", AppCategory.COMMUNICATION, [AppPlatform.DESKTOP])
        ents = reg.list_apps(category=AppCategory.ENTERTAINMENT)
        assert len(ents) == 1

    def test_list_apps_enabled_only(self):
        reg = AppRegistry()
        app1 = reg.install("App1", AppCategory.UTILITIES, [AppPlatform.MOBILE])
        app2 = reg.install("App2", AppCategory.UTILITIES, [AppPlatform.MOBILE])
        reg.disable(app2.app_id)
        enabled = reg.list_apps(enabled_only=True)
        assert len(enabled) == 1

    def test_app_not_found_raises(self):
        reg = AppRegistry()
        with pytest.raises(KeyError):
            reg.get_app("app_9999")


class TestBrowserToolkit:
    def test_add_tool(self):
        bt = BrowserToolkit()
        tool = bt.add_tool("Dashboard", "https://example.com", "Control panel")
        assert tool.name == "Dashboard"

    def test_list_tools(self):
        bt = BrowserToolkit()
        bt.add_tool("Tool1", "https://example.com/1")
        bt.add_tool("Tool2", "https://example.com/2")
        assert len(bt.list_tools()) == 2

    def test_remove_tool(self):
        bt = BrowserToolkit()
        tool = bt.add_tool("Tool", "https://example.com")
        bt.remove_tool(tool.tool_id)
        assert len(bt.list_tools()) == 0

    def test_get_tool_not_found_raises(self):
        bt = BrowserToolkit()
        with pytest.raises(KeyError):
            bt.get_tool("btool_9999")


class TestSmartDeviceHub:
    def test_add_device(self):
        hub = SmartDeviceHub()
        dev = hub.add_device(
            "Smart Light", SmartDeviceProtocol.ZIGBEE, room="Living Room"
        )
        assert dev.name == "Smart Light"

    def test_set_online(self):
        hub = SmartDeviceHub()
        dev = hub.add_device("Thermostat", SmartDeviceProtocol.MATTER)
        hub.set_online(dev.device_id, True)
        assert hub.get_device(dev.device_id).online is True

    def test_update_state(self):
        hub = SmartDeviceHub()
        dev = hub.add_device("Light", SmartDeviceProtocol.WIFI)
        hub.update_state(dev.device_id, {"on": True, "brightness": 80})
        assert hub.get_device(dev.device_id).state["on"] is True

    def test_list_by_room(self):
        hub = SmartDeviceHub()
        hub.add_device("Light", SmartDeviceProtocol.ZIGBEE, room="Kitchen")
        hub.add_device("TV", SmartDeviceProtocol.WIFI, room="Living Room")
        kitchen = hub.list_devices(room="Kitchen")
        assert len(kitchen) == 1

    def test_device_not_found_raises(self):
        hub = SmartDeviceHub()
        with pytest.raises(KeyError):
            hub.get_device("sd_9999")


class TestNvidiaToolsHub:
    def test_list_tools_returns_all(self):
        hub = NvidiaToolsHub()
        tools = hub.list_tools()
        assert len(tools) == len(NVIDIA_TOOLS)

    def test_markup_applied(self):
        hub = NvidiaToolsHub()
        for tool in hub.list_tools():
            assert tool["markup_pct"] == NVIDIA_MARKUP_PCT

    def test_activate_tool(self):
        hub = NvidiaToolsHub()
        result = hub.activate_tool("cuda")
        assert result["activated"] is True

    def test_deactivate_tool(self):
        hub = NvidiaToolsHub()
        hub.activate_tool("cuda")
        result = hub.deactivate_tool("cuda")
        assert result["activated"] is False

    def test_get_activated_tools(self):
        hub = NvidiaToolsHub()
        hub.activate_tool("cuda")
        hub.activate_tool("tensorrt")
        activated = hub.get_activated_tools()
        assert len(activated) == 2

    def test_unknown_tool_raises(self):
        hub = NvidiaToolsHub()
        with pytest.raises(KeyError):
            hub.activate_tool("nonexistent_tool")


class TestStarlinkManager:
    def test_list_plans(self):
        mgr = StarlinkManager()
        plans = mgr.list_plans()
        assert len(plans) == len(STARLINK_PLANS)

    def test_markup_applied_to_plans(self):
        mgr = StarlinkManager()
        for plan in mgr.list_plans():
            expected = round(
                plan["base_monthly_usd"] * (1 + STARLINK_MARKUP_PCT / 100), 2
            )
            assert plan["marked_up_monthly_usd"] == expected

    def test_create_subscription(self):
        mgr = StarlinkManager()
        sub = mgr.create_subscription("Alice", "residential")
        assert sub.client_name == "Alice"
        assert sub.active is True

    def test_cancel_subscription(self):
        mgr = StarlinkManager()
        sub = mgr.create_subscription("Bob", "roam")
        mgr.cancel_subscription(sub.subscription_id)
        assert not mgr.get_subscription(sub.subscription_id).active

    def test_list_active_subscriptions(self):
        mgr = StarlinkManager()
        mgr.create_subscription("A", "residential")
        sub2 = mgr.create_subscription("B", "business")
        mgr.cancel_subscription(sub2.subscription_id)
        active = mgr.list_subscriptions(active_only=True)
        assert len(active) == 1

    def test_invalid_plan_raises(self):
        mgr = StarlinkManager()
        with pytest.raises(ValueError):
            mgr.create_subscription("X", "invalid_plan")

    def test_subscription_not_found_raises(self):
        mgr = StarlinkManager()
        with pytest.raises(KeyError):
            mgr.get_subscription("sl_9999")


# ===========================================================================
# 6. BuddyOS (integration)
# ===========================================================================


class TestBuddyOS:
    def test_instantiation_free_tier(self):
        buddy = BuddyOS(tier=Tier.FREE)
        assert buddy.tier == Tier.FREE

    def test_instantiation_pro_tier(self):
        buddy = BuddyOS(tier=Tier.PRO)
        assert buddy.config.price_usd_monthly == 49.0

    def test_boot_log_populated(self):
        buddy = BuddyOS()
        assert len(buddy.get_boot_log()) > 0

    def test_system_status_keys(self):
        buddy = BuddyOS(tier=Tier.PRO)
        status = buddy.system_status()
        for key in (
            "tier",
            "connected_devices",
            "bluetooth_paired",
            "active_cast_sessions",
            "installed_apps",
        ):
            assert key in status

    def test_connect_device_convenience(self):
        buddy = BuddyOS(tier=Tier.PRO)
        device = buddy.connect_device("iPhone", DeviceType.PHONE, DevicePlatform.APPLE)
        assert device.is_connected()

    def test_pair_bluetooth_convenience(self):
        buddy = BuddyOS(tier=Tier.PRO)
        dev = buddy.pair_bluetooth("AA:BB:CC:DD:EE:FF", "Headphones")
        assert dev.state == BluetoothState.CONNECTED

    def test_cast_to_screen_convenience(self):
        buddy = BuddyOS(tier=Tier.PRO)
        session = buddy.cast_to_screen(
            "Living Room TV", CastProtocol.GOOGLE_CAST, "https://example.com/video.mp4"
        )
        assert session.state == CastState.CASTING

    def test_describe_tier(self):
        buddy = BuddyOS(tier=Tier.FREE)
        desc = buddy.describe_tier()
        assert "Free" in desc
        assert "$0.00" in desc

    def test_chat_status(self):
        buddy = BuddyOS()
        resp = buddy.chat("status")
        assert resp["response"] == "buddy_os"
        assert "data" in resp

    def test_chat_device(self):
        buddy = BuddyOS()
        resp = buddy.chat("show devices")
        assert "device" in resp["message"].lower()

    def test_chat_bluetooth(self):
        buddy = BuddyOS()
        resp = buddy.chat("bluetooth status")
        assert resp["response"] == "buddy_os"

    def test_chat_cast(self):
        buddy = BuddyOS()
        resp = buddy.chat("cast to screen")
        assert resp["response"] == "buddy_os"

    def test_chat_apps(self):
        buddy = BuddyOS()
        resp = buddy.chat("list apps")
        assert "app" in resp["message"].lower()

    def test_chat_starlink(self):
        buddy = BuddyOS()
        resp = buddy.chat("tell me about starlink")
        assert "plans" in resp["data"]

    def test_chat_nvidia(self):
        buddy = BuddyOS()
        resp = buddy.chat("nvidia tools")
        assert "nvidia_tools" in resp["data"]

    def test_chat_tier(self):
        buddy = BuddyOS()
        resp = buddy.chat("upgrade plan")
        assert "Buddy OS" in resp["message"]

    def test_chat_default(self):
        buddy = BuddyOS()
        resp = buddy.chat("hello")
        assert resp["response"] == "buddy_os"

    def test_tier_error_free_feature_blocked(self):
        buddy = BuddyOS(tier=Tier.FREE)
        with pytest.raises(BuddyOSTierError):
            buddy._require_feature(FEATURE_WHITE_LABEL)

    def test_register_with_buddy(self):
        from BuddyAI.buddy_bot import BuddyBot

        orchestrator = BuddyBot()
        buddy_os = BuddyOS(tier=Tier.PRO)
        buddy_os.register_with_buddy(orchestrator)
        assert "buddy_os" in orchestrator.list_bots()

    def test_default_browser_tools_loaded(self):
        buddy = BuddyOS()
        tools = buddy.browser.list_tools()
        assert len(tools) >= 2
