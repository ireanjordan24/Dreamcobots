"""DreamCo Buddy OS package."""

from bots.buddy_os.buddy_os import BuddyOS, BuddyOSError, BuddyOSTierError
from bots.buddy_os.tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers
from bots.buddy_os.device_manager import (
    DeviceManager,
    Device,
    DeviceType,
    DevicePlatform,
    DeviceStatus,
)
from bots.buddy_os.bluetooth_engine import (
    BluetoothEngine,
    BluetoothDevice,
    BluetoothProfileType,
    BluetoothState,
    FileTransfer,
)
from bots.buddy_os.cast_engine import (
    CastEngine,
    CastReceiver,
    CastSession,
    CastProtocol,
    CastState,
    ContentType,
)
from bots.buddy_os.app_framework import (
    AppRegistry,
    BrowserToolkit,
    SmartDeviceHub,
    NvidiaToolsHub,
    StarlinkManager,
    AppCategory,
    AppPlatform,
    SmartDeviceProtocol,
)

__all__ = [
    "BuddyOS",
    "BuddyOSError",
    "BuddyOSTierError",
    "Tier",
    "TierConfig",
    "get_tier_config",
    "get_upgrade_path",
    "list_tiers",
    "DeviceManager",
    "Device",
    "DeviceType",
    "DevicePlatform",
    "DeviceStatus",
    "BluetoothEngine",
    "BluetoothDevice",
    "BluetoothProfileType",
    "BluetoothState",
    "FileTransfer",
    "CastEngine",
    "CastReceiver",
    "CastSession",
    "CastProtocol",
    "CastState",
    "ContentType",
    "AppRegistry",
    "BrowserToolkit",
    "SmartDeviceHub",
    "NvidiaToolsHub",
    "StarlinkManager",
    "AppCategory",
    "AppPlatform",
    "SmartDeviceProtocol",
]
