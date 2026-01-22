from gpt4all import GPT4All
from pathlib import Path


MODEL_PATH = Path(__file__).resolve().parent.parent / "models"
MODEL_NAME = "orca-mini-3b-gguf2-q4_0.gguf"


class LocalAIEngine:
    _model = None

    def __init__(self):
        if LocalAIEngine._model is None:
            print("-" * 50)
            print("AI SYSTEM: Initializing Local Model (orca-mini-3b)...")
            print("NOTE: You may see 'Failed to load...dll' errors below.")
            print("      These are NORMAL if you don't have a specific NVIDIA GPU.")
            print("      The system will automatically fall back to CPU mode.")
            print("-" * 50)
            
            try:
                LocalAIEngine._model = GPT4All(
                    model_name=MODEL_NAME,
                    model_path=str(MODEL_PATH),
                    allow_download=True,
                )
                print("Local AI Model loaded successfully.")
            except Exception as e:
                print(f"CRITICAL: Failed to load Local AI Model: {e}")

    def generate(self, prompt: str, context: str = "") -> str:
        system_prompt = (
            "You are SysSentinel AI, a system diagnostics assistant.\n"
            "Give practical, cautious advice.\n"
            "Do not suggest destructive actions unless explicitly asked.\n\n"
        )

        full_prompt = (
            system_prompt
            + f"Context:\n{context}\n\n"
            + f"User Question:\n{prompt}\n\n"
            + "Answer:"
        )

        try:
            if LocalAIEngine._model is None:
                return "Error: AI Model not loaded (check console logs)."

            with LocalAIEngine._model.chat_session():
                response = LocalAIEngine._model.generate(
                    full_prompt,
                    max_tokens=256,
                    temp=0.2,
                )
            return response.strip()

        except Exception as e:
            return (
                "Local AI failed to respond.\n"
                "Make sure the model file is bundled correctly.\n\n"
                f"Error: {e}"
            )
