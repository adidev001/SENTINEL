import asyncio
from datetime import datetime

import flet as ft
from app.ui.tray import start_tray

from app.core.event_bus import EventBus
from app.core.scheduler import Scheduler
from app.core.state import AppState

from app.collectors.cpu import collect_cpu
from app.collectors.memory import collect_memory
from app.collectors.disk import collect_disk
from app.collectors.network import collect_network
from app.collectors.gpu import collect_gpu

from app.storage.writer import write_metrics
from app.storage.retention import prune_old_data
from app.storage.reader import read_recent_metrics

from app.ml.features import batch_features, FEATURE_ORDER
from app.ml.normalizer import FeatureNormalizer
from app.ml.anomaly import AnomalyDetector
from app.ml.enhanced_forecaster import EnhancedResourceForecaster
from app.ml.overload_detector import OverloadDetector

from app.intelligence.anomaly_engine import interpret_anomalies
from app.intelligence.forecast_engine import interpret_forecast
from app.intelligence.health_state import compute_health_state

from app.logic.decision_engine import decide_actions
from app.logic.enhanced_decision_engine import enhanced_decide_actions
from app.logic.action_router import map_actions_to_commands

from app.notifications.rules import should_notify
from app.notifications.throttle import NotificationThrottle
from app.notifications.toast import show_toast

from app.ui.app_shell import run_ui
from app.ui.theme import DARK_THEME, Palette


# -------------------------------------------------
# Collectors → EventBus
# -------------------------------------------------
async def collect_and_publish(event_bus: EventBus) -> None:
    payload = {}
    payload.update(collect_cpu())
    payload.update(collect_memory())
    payload.update(collect_disk())
    payload.update(collect_network())
    payload.update(collect_gpu())

    await event_bus.publish({
        "type": "metrics",
        "timestamp": datetime.utcnow().isoformat(),
        "payload": payload
    })


# -------------------------------------------------
# EventBus → Storage
# -------------------------------------------------
async def storage_consumer(event_bus: EventBus) -> None:
    while True:
        event = await event_bus.subscribe()
        if event.get("type") != "metrics":
            continue

        p = event["payload"]
        write_metrics(
            timestamp=event["timestamp"],
            data={
                "cpu_percent": p.get("cpu_percent"),
                "memory_used_mb": p.get("used_mb"),
                "memory_percent": p.get("percent"),
                "disk_percent": p.get("percent_used"),
                "read_mb": p.get("read_mb_s"),
                "write_mb": p.get("write_mb_s"),
                "upload_kb": p.get("upload_kb"),
                "download_kb": p.get("download_kb"),
                "gpu_percent": p.get("gpu_percent"),
            }
        )


# -------------------------------------------------
# Storage → ML → Intelligence → Logic → Notifications
# -------------------------------------------------
async def decision_pipeline(
    detector: AnomalyDetector,
    normalizer: FeatureNormalizer,
    forecaster: EnhancedResourceForecaster,
    overload_detector: OverloadDetector,
    throttle: NotificationThrottle
) -> None:
    metrics = read_recent_metrics(minutes=10)
    if len(metrics) < 5:
        return

    X = batch_features(metrics)
    Xn = normalizer.fit_transform(X)

    if not detector.fitted:
        detector.fit(Xn)

    scores = detector.score(Xn)
    anomalies = interpret_anomalies(
        scores[-len(FEATURE_ORDER):],
        FEATURE_ORDER
    )

    # Multi-resource forecasting
    if hasattr(forecaster, 'predict_all_resources'):
        all_forecasts = forecaster.predict_all_resources(metrics)
    else:
        all_forecasts = {}

    # Overload prediction
    overload_risk = overload_detector.predict_overload_risk(all_forecasts)

    # Legacy memory forecast for health state (compat)
    mem_series = [
        m["memory_percent"]
        for m in metrics
        if m.get("memory_percent") is not None
    ]
    forecast_raw = forecaster.predict(values=mem_series)
    forecast = interpret_forecast(
        resource="memory",
        prediction=forecast_raw,
        limit=95.0
    )

    health = compute_health_state(anomalies, [forecast])

    # Enhanced decision making
    decision = enhanced_decide_actions(
        health_state=health,
        anomalies=anomalies,
        forecasts=[forecast],
        overload_predictions=overload_risk
    )

    if should_notify(decision) and throttle.allow():
        intents = map_actions_to_commands(decision.get("actions", []))
        show_toast(
            title="SysSentinel AI",
            message=f"System health: {health['overall_status']}",
            actions=[i["command_id"] for i in intents]
        )


# -------------------------------------------------
# Backend bootstrap
# -------------------------------------------------
async def backend_main():
    from app.storage.database import initialize_database
    initialize_database()

    event_bus = EventBus()
    scheduler = Scheduler()
    app_state = AppState()

    detector = AnomalyDetector()
    normalizer = FeatureNormalizer()
    forecaster = EnhancedResourceForecaster()
    overload_detector = OverloadDetector()
    throttle = NotificationThrottle(cooldown_seconds=300)

    scheduler.every(2, lambda: collect_and_publish(event_bus))
    scheduler.every(3600, lambda: asyncio.to_thread(prune_old_data))
    scheduler.every(
        30,
        lambda: decision_pipeline(
            detector,
            normalizer,
            forecaster,
            overload_detector,
            throttle
        )
    )

    asyncio.create_task(storage_consumer(event_bus))

    while True:
        await asyncio.sleep(1)


# -------------------------------------------------
# Loading Page Integration
# -------------------------------------------------


# -------------------------------------------------
# UI + Backend entrypoint
# -------------------------------------------------
# -------------------------------------------------
# UI + Backend entrypoint
# -------------------------------------------------
async def app_entry(page: ft.Page):
    """Main app entry point."""
    page.title = "SysSentinel AI"
    page.window_width = 1280
    page.window_height = 850
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = Palette.BG_DARK
    
    # Initialize backend components holder
    page.backend_components = {}
    
    # Start tray
    start_tray(lambda: page.window_show())
    
    # Start backend logic
    asyncio.create_task(backend_main())
    
    # Run main UI
    run_ui(page)


if __name__ == "__main__":
    ft.app(target=app_entry, assets_dir="assets")
