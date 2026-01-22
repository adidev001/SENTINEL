# SysSentinel AI 🛡️

**SysSentinel AI** is an intelligent, real-time system monitoring agent for Windows. It combines live performance metrics with an integrated **AI Assistant** (RAG, Local LLM, and Cloud AI) to help you not just *see* what your computer is doing, but *understand* and *manage* it actively.

![Dashboard Preview](assets/background.png)

## ✨ Key Features

### 🖥️ Real-Time Monitoring
*   **Cpu, Memory, Disk, Network, GPU** metrics visualized instantly.
*   **Health Status Badge** detects anomalies automatically.
*   **Disk Scanner** to find space-hogging folders.

### 🧠 Triple-Mode AI Assistant
1.  **RAG Mode (Offline)**: Instant answers about *your* specific system state (e.g., "What is using the most RAM?").
2.  **Local AI (Offline)**: Runs `orca-mini-3b` locally for private, general-purpose chat.
3.  **Cloud AI (Online)**: Connects to OpenRouter (GPT-4 class models) for advanced reasoning.

### ⚡ Process Management
*   **Segregated Views**: Separate tabs for **User Apps** vs **Background Services**.
*   **Smart Actions**: "Ask AI" about any suspicious process or **Terminate** it safely.
*   **Auto-Restart**: Configurable automation to restart critical apps if they crash.

### 🔮 Predictive Analytics
*   **Resource Forecasting**: Predicting CPU/Memory usage 10 minutes into the future.
*   **Anomaly Detection**: Machine Learning (Isolation Forest) models to flag unusual behavior.

## 🚀 Installation

### Prerequisites
*   Python 3.10+
*   Windows 10/11

### Setup
1.  Clone the repository:
    ```bash
    git clone https://github.com/adidev001/SENTINEL.git
    cd SENTINEL
    ```

2.  Create a virtual environment (recommended):
    ```bash
    python -m venv .venv
    .\.venv\Scripts\Activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## 🎮 Usage

Run the application:
```bash
python main.py
```

*   **Dashboard**: View live stats and system health.
*   **Performance**: Manage running processes (kill apps, view stats).
*   **Analytics**: See AI predictions for resource usage.
*   **AI Chat**: Talk to your system. Ask "Why is my PC slow?" or "Scan drive D:".
*   **Settings**: Configure AI modes, alerts, and themes.

## 🛠️ Tech Stack
*   **UI**: [Flet](https://flet.dev) (Flutter for Python)
*   **AI**: `gpt4all` (Local), `langchain` (RAG), `openai` (Cloud client)
*   **ML**: `scikit-learn` (Anomaly Detection), `numpy`
*   **System**: `psutil`, `winotify`

## ❤️ Credits
Made with love by **Devansh** and **Jahnavi**.
