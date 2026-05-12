# DreamCo Installation Guide

## Full Installation for Contributors

### System Requirements
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.11 | 3.12 |
| Node.js | 18 | 20 LTS |
| RAM | 4 GB | 8 GB |
| Disk | 2 GB | 10 GB |
| Docker | 24 | Latest |

---

## Installation Options

### Option A — Python Only (Lightweight)
```bash
git clone https://github.com/DreamCo-Technologies/Dreamcobots.git
cd Dreamcobots
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python tools/check_bot_framework.py
```

### Option B — Full Stack (Python + Node.js Control Tower)
```bash
git clone https://github.com/DreamCo-Technologies/Dreamcobots.git
cd Dreamcobots

# Python dependencies
pip install -r requirements.txt

# Node.js dependencies (for Control Tower)
npm install

# Start Control Tower backend
cd dreamco-control-tower/backend
npm install
node server.js &

# Start Control Tower frontend
cd ../frontend
npm install
npm start
```

### Option C — Docker (Fully Containerized)
```bash
git clone https://github.com/DreamCo-Technologies/Dreamcobots.git
cd Dreamcobots
docker-compose up --build
```

---

## Verifying Installation

```bash
# Check Python bots
python3 -m pytest tests/ --ignore=tests/test_backend.py \
    --ignore=tests/test_web_dashboard.py -q

# Check Node.js (if installed)
npm run test

# Check bot framework compliance
python tools/check_bot_framework.py
```

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: framework` | Run from repo root; add `.` to PYTHONPATH |
| `pip: command not found` | Use `pip3` or install pip |
| `No module named pytest` | `pip install pytest` |
| `Docker: permission denied` | Add user to docker group; or use `sudo` |
| Port 3000 in use | Kill existing process or change port in server.js |

_See also: [SETUP.md](../../../SETUP.md) for platform-specific instructions._
