# app/core/state.py

from dataclasses import dataclass

@dataclass
class AppState:
    """
    Global application state.
    """
    theme: str = "light"      # light | dark
    llm_mode: str = "local"   # local | cloud
    offline: bool = False

    def toggle_theme(self) -> None:
        self.theme = "dark" if self.theme == "light" else "light"

    def set_llm_mode(self, mode: str) -> None:
        if mode not in ("local", "cloud"):
            raise ValueError("Invalid LLM mode")
        self.llm_mode = mode

    def set_offline(self, offline: bool) -> None:
        self.offline = offline
