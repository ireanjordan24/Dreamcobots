# Buddy OS

Advanced operating-system-like bot for the DreamCobots ecosystem.

## Overview

Buddy OS runs on **any device** — smartphone, tablet, desktop, smart TV, or gaming console — and provides a unified control layer for device management, Bluetooth connectivity, screen casting, app management, smart-home integrations, NVIDIA AI tools, and Starlink connectivity.

## Features

| Module | Description |
|---|---|
| **Device Manager** | Universal compatibility: TVs, gaming consoles, phones, tablets, computers (Apple, Google, Windows, Linux, Samsung, Sony, Microsoft) |
| **Bluetooth Engine** | Device discovery, pairing, trust, connection, and file transfer (OPP/FTP) |
| **Cast Engine** | Screen casting via Google Cast, Apple AirPlay, Miracast, HDMI, DLNA |
| **App Registry** | Install, enable, disable apps across mobile, desktop, web, TV, and console platforms |
| **Browser Toolkit** | Browser-based tool shortcuts and web-app management |
| **Smart Device Hub** | IoT/smart-home control via IFTTT, Matter, Zigbee, Z-Wave, Wi-Fi, Thread |
| **NVIDIA Tools Hub** | Isaac SDK, Jetson, Omniverse, CUDA, TensorRT, Triton, NeMo, RAPIDS — with 25% markup |
| **Starlink Manager** | Satellite internet plans and subscription management with 25% markup resale |

## Tiers

| Tier | Price | Paired Devices | Cast Targets |
|---|---|---|---|
| Free | $0/month | 3 | 1 |
| Pro | $49/month | 25 | 10 |
| Enterprise | $199/month | Unlimited | Unlimited |

## Quick Start

```python
from bots.buddy_os import BuddyOS, Tier
from bots.buddy_os import DeviceType, DevicePlatform, CastProtocol, ContentType

# Create Buddy OS
buddy = BuddyOS(tier=Tier.PRO)

# Connect a device
phone = buddy.device_manager.register_device(
    "My iPhone", DeviceType.PHONE, DevicePlatform.APPLE, os_version="17.0"
)
buddy.device_manager.connect(phone.device_id)

# Pair a Bluetooth device
buddy.bluetooth.add_discovered_device("AA:BB:CC:DD:EE:FF", "JBL Charge 5", rssi=-55)
buddy.bluetooth.pair_device("AA:BB:CC:DD:EE:FF")
buddy.bluetooth.connect("AA:BB:CC:DD:EE:FF")

# Cast to a screen
recv = buddy.cast.add_receiver("Living Room TV", CastProtocol.GOOGLE_CAST, ip_address="192.168.1.50")
session = buddy.cast.start_cast(recv.receiver_id, ContentType.VIDEO, "https://example.com/video.mp4")

# System status
print(buddy.system_status())

# Chat interface (BuddyAI compatible)
response = buddy.chat("Show me connected devices")
print(response["message"])

# Register with BuddyAI orchestrator
from BuddyAI.buddy_bot import BuddyBot
orchestrator = BuddyBot()
buddy.register_with_buddy(orchestrator)
```

## Directory Structure

```
bots/buddy_os/
├── buddy_os.py          # Main BuddyOS class
├── tiers.py             # FREE/PRO/ENTERPRISE tiers
├── device_manager.py    # Universal device compatibility
├── bluetooth_engine.py  # Bluetooth pairing and file transfer
├── cast_engine.py       # Screen casting (Cast/AirPlay/Miracast/HDMI)
├── app_framework.py     # App registry, browser tools, smart devices,
│                        #   NVIDIA tools, Starlink manager
├── __init__.py
└── README.md
```
