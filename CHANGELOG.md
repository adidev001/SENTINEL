# CHANGELOG

All notable changes to SysSentinel AI will be documented in this file.

## [Unreleased]

### Added
- Anomaly history tracking in SQLite database
- Anomaly visualization in Analytics page
- Alert threshold integration with main metrics loop
- GPU graceful fallback for systems without discrete GPU

### Changed
- Analytics page now shows anomaly count and history
- Settings page alert thresholds now functional

### Fixed
- GPU card shows "N/A" instead of crashing on unsupported systems

---

## [1.0.0] - 2026-01-23

### Added
- Initial release with all core features
- Real-time CPU, Memory, Disk, Network, GPU monitoring
- AI Chat with RAG, Local AI, and Cloud AI modes
- Process management with Apps/Background segregation
- Predictive analytics using Linear Regression
- Anomaly detection using Isolation Forest
- Windows toast notifications
- CSV data export
- Settings page with AI mode selector
- Credits footer with GitHub link

### Technical
- Flet UI framework
- SQLite for metrics storage
- scikit-learn for ML models
- gpt4all for local AI
