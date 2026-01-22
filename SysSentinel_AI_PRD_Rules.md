# SysSentinel AI  
## Product Requirements Document (PRD) — Rules & Governance

---

## 1. Purpose of This Document

This document defines the **non-negotiable rules** governing the design, implementation, and evolution of **SysSentinel AI**.

It exists to:
- Prevent scope creep
- Avoid architectural contradictions
- Enforce privacy-first behavior
- Ensure future features do not break existing guarantees
- Serve as the final arbiter in design disputes

If a feature violates this document, the feature is **wrong**, not the document.

---

## 2. Product Vision

SysSentinel AI is a **Windows-native, proactive system intelligence tool** that:
- Monitors system behavior continuously
- Detects anomalies before failures occur
- Explains system issues in plain English
- Operates **offline by default**
- Never leaks system data without explicit user consent

This is **not** a generic system monitor.  
This is **diagnostics + foresight + explainability**.

---

## 3. Core Product Principles (Hard Rules)

### 3.1 Privacy Is the Default
- All system data is processed **locally by default**
- No telemetry leaves the machine unless explicitly enabled
- API keys are never stored in plaintext
- No silent cloud fallbacks

### 3.2 Offline First, Online Optional
- Meaningful operation without internet
- Monitoring, analytics, anomaly detection, and AI explanations must work offline

### 3.3 Stability Over Cleverness
- Reliability beats novelty
- One subsystem failure must not cascade
- Graceful degradation is mandatory

### 3.4 Predictive, Not Reactive
- Forecast issues **before** failure
- Minimum forecast horizon: 5 minutes
- Target horizon: 10 minutes

---

## 4. Functional Requirements

### 4.1 Data Collection
- Polling interval: 2 seconds
- Metrics: CPU, Memory, Disk, Network, GPU
- CPU overhead < 1%

### 4.2 Data Retention
- Sliding window: 10 days
- Hourly pruning
- No option to disable pruning

### 4.3 Anomaly Detection
- Unsupervised learning only
- Per-machine baseline
- Explainable anomaly scores

### 4.4 Forecasting
- Lightweight models only
- Include time-to-threshold and confidence

### 4.5 Health States
- Green: Normal
- Yellow: Warning
- Red: Critical
- Computable without AI

---

## 5. AI Assistant Rules

### 5.1 Role
- Explain causes
- Suggest safe actions
- Translate metrics to human language

### 5.2 Local AI
- Fully offline
- Model bundled with app
- No runtime downloads
- Lazy loading
- Clear failure messaging

### 5.3 Cloud AI (Future)
- Disabled by default
- Explicit user opt-in
- Clear data disclosure
- Instant disable

### 5.4 Context Injection
- Last 5–10 minutes of logs
- Relevant metrics and process info
- Bounded context size

---

## 6. UI / UX Rules

### 6.1 Performance
- ~60 FPS UI
- No blocking on UI thread

### 6.2 Navigation
- Stateless pages
- Shared state in app shell

### 6.3 Dark Mode
- Mandatory
- Toggle in Settings
- No restart required

### 6.4 Placeholders
- Allowed temporarily
- Must map to PRD items
- Must be removed eventually

---

## 7. Security Rules
- No plaintext secrets
- OS keyring only
- No automatic command execution
- User confirmation required

---

## 8. Platform Constraints
- Windows 10/11 only
- NVIDIA GPU support
- SQLite (WAL)
- Python 3.10+
- Flet UI

---

## 9. Non-Goals
- Antivirus
- Kernel drivers
- Cloud dashboards
- Mobile apps
- Cross-OS support

---

## 10. Definition of Done
A feature is done only when:
- It follows this PRD
- Works offline if applicable
- Preserves privacy
- Fails safely

---

## 11. Change Control
- Explicit updates only
- No silent rule changes
- No “fix later” violations

---

**End of Document**
