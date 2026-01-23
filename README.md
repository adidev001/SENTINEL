# SENTINEL

<p align="center">
  <img src="assets/icon.png" alt="SENTINEL Logo" width="128"/>
</p>

<p align="center">
  <b>AI-Powered System Monitoring & Diagnostics</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/Flet-0.21+-purple?logo=flutter" alt="Flet"/>
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows" alt="Windows"/>
  <img src="https://img.shields.io/badge/AI-GPT4All-green" alt="AI"/>
</p>

---

## Overview

SENTINEL is a standalone Windows application that provides real-time system monitoring with AI-powered diagnostics. It combines beautiful cyberpunk-themed visualizations with machine learning anomaly detection to help you understand and optimize your system's performance.

---

## ✨ Features

### 📊 Real-Time Monitoring
- **CPU Usage** - Live percentage with historical charts
- **Memory** - Used/Total with trend analysis
- **Disk** - Storage consumption and I/O rates
- **Network** - Upload/Download speeds
- **GPU** - NVIDIA GPU utilization (via nvidia-smi)

### 🧠 AI Intelligence
- **Local AI Chat** - Offline diagnostics using GPT4All (Orca Mini 3B)
- **Cloud AI** - Optional Google Gemini integration for enhanced analysis
- **Anomaly Detection** - ML-powered unusual behavior detection
- **Predictive Forecasting** - Resource usage prediction
- **Overload Prevention** - Early warning system for system stress

### 🔔 Smart Alerts
- **Windows Toast Notifications** - Native alert popups
- **Email Notifications** - SMTP integration (optional)
- **Webhook Support** - Custom HTTP callbacks
- **Configurable Thresholds** - CPU, Memory, Disk warning levels

### ⚙️ Automation
- **Process Auto-Restart** - Monitor and restart critical processes
- **Priority Adjustment** - Automatic process prioritization
- **Custom Metrics** - Define your own tracking commands

### 🔒 Security
- **Windows Credential Manager** - API keys stored securely via Keyring
- **No Plain-Text Secrets** - Sensitive data never written to disk

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         SENTINEL.exe                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Frontend   │    │   Backend    │    │   Storage    │      │
│  │   (Flet UI)  │◄──►│  (AsyncIO)   │◄──►│  (SQLite)    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Dashboard   │    │  Collectors  │    │   Metrics    │      │
│  │  Analytics   │    │  CPU/Mem/GPU │    │   Anomalies  │      │
│  │  AI Chat     │    │  Disk/Net    │    │   Alerts     │      │
│  │  Settings    │    └──────────────┘    └──────────────┘      │
│  └──────────────┘           │                                   │
│                             ▼                                   │
│                    ┌──────────────────┐                         │
│                    │   ML Pipeline    │                         │
│                    │  ┌────────────┐  │                         │
│                    │  │ Normalizer │  │                         │
│                    │  │ Detector   │  │                         │
│                    │  │ Forecaster │  │                         │
│                    │  └────────────┘  │                         │
│                    └──────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
              │
              ▼
    %APPDATA%/SENTINEL/
    ├── data/sys_sentinel.db    (Metrics Database)
    ├── models/                 (AI Models)
    └── logs/debug.log          (Debug Logs)
```

---

## 📁 Project Structure

```
sentinal/
├── main.py                    # Application entry point
├── build.ps1                  # Build script for standalone EXE
├── requirements.txt           # Python dependencies
├── assets/
│   ├── icon.ico               # Application icon
│   ├── icon.png               # Icon source
│   └── background.png         # UI background
├── app/
│   ├── core/                  # Event bus, scheduler, state
│   ├── collectors/            # CPU, Memory, Disk, Network, GPU
│   ├── storage/               # SQLite database, reader, writer
│   ├── ml/                    # Anomaly detection, forecasting
│   ├── intelligence/          # AI engines, health state
│   ├── logic/                 # Decision engine, action router
│   ├── notifications/         # Toast, throttle, rules
│   ├── alerts/                # Alert manager
│   ├── automation/            # Process automation
│   ├── ai/                    # Model manager (GPT4All)
│   └── ui/
│       ├── components/        # MetricCard, HealthBadge, Charts
│       ├── pages/             # Dashboard, Analytics, AI, Settings
│       ├── app_shell.py       # Main UI shell
│       ├── sidebar.py         # Navigation
│       └── theme.py           # Cyberpunk color palette
└── dist/
    └── SENTINEL.exe           # Standalone executable
```

---

## 🚀 Quick Start (Standalone)

### Option 1: Run the Pre-Built Executable

1. Navigate to the `dist/` folder:
   ```
   d:\project\sentinal\dist\
   ```

2. Double-click **`SENTINEL.exe`** to launch.

3. The app stores data in:
   ```
   %APPDATA%\SENTINEL\
   ```

### Option 2: Run from Source

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/adidev001/SENTINEL.git
   cd SENTINEL
   ```

2. **Create virtual environment:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```powershell
   python main.py
   ```

---

## 🔧 Building the Standalone EXE

### Prerequisites
- Python 3.11+
- Virtual environment with all dependencies installed

### Build Command

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run build script
.\build.ps1
```

### Build Output
- Creates `dist/SENTINEL.exe` (~150MB)
- Includes all dependencies and assets
- Single-file executable (no installation required)

---

## ⚙️ Configuration

### AI Modes (Settings Page)
| Mode | Description |
|------|-------------|
| **Local** | Uses GPT4All (Orca Mini 3B) - runs offline, ~4GB model download |
| **Cloud** | Uses Google Gemini API - requires API key |
| **Off** | Disables AI diagnostics |

### Alert Thresholds
| Metric | Warning | Critical |
|--------|---------|----------|
| CPU | 75% | 90% |
| Memory | 80% | 95% |
| Disk | 80% | 95% |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **UI Framework** | [Flet](https://flet.dev) (Flutter for Python) |
| **Language** | Python 3.11 |
| **Database** | SQLite3 |
| **ML** | Scikit-learn (IsolationForest) |
| **Local AI** | GPT4All (GGUF models) |
| **Cloud AI** | Google Gemini API |
| **System Metrics** | psutil |
| **GPU Metrics** | nvidia-smi (subprocess) |
| **Notifications** | win11toast |
| **Credential Storage** | keyring (Windows Credential Manager) |
| **Packaging** | PyInstaller + Flet Pack |

---

## 📝 Data Storage

All application data is stored in:
```
%APPDATA%\SENTINEL\
├── data\
│   └── sys_sentinel.db    # SQLite metrics database
├── models\
│   └── orca-mini-3b-gguf2-q4_0.gguf  # AI model (downloaded on first use)
└── logs\
    └── debug.log          # Debug output
```

---

## 🐛 Troubleshooting

### Dashboard shows 0% metrics
- Ensure the app has been running for at least 5 seconds
- Check `%APPDATA%\SENTINEL\logs\debug.log` for errors

### AI Chat not working
- For Local mode: Check if the model is downloaded in Settings
- For Cloud mode: Verify your Gemini API key is entered correctly

### GPU shows N/A
- Ensure NVIDIA drivers are installed
- `nvidia-smi` must be accessible from PATH

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 👤 Author

**Devansh (adidev001)**

- GitHub: [@adidev001](https://github.com/adidev001)

---

<p align="center">
  Made with ❤️ and Python
</p>
