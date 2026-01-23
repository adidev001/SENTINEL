from app.ai.model_manager import ModelManager, MODEL_NAME

MODEL_NAME = MODEL_NAME # keep for internal refs if any

class LocalAIEngine:
    _model = None
    _init_attempted = False

    def __init__(self):
        if LocalAIEngine._model is None and not LocalAIEngine._init_attempted:
            LocalAIEngine._init_attempted = True
            
            if not ModelManager.is_model_installed():
                print("AI SYSTEM: Local model not found. Skipping initialization.")
                return

            print("-" * 50)
            print("AI SYSTEM: Initializing Local Model...")
            print("-" * 50)
            
            try:
                LocalAIEngine._model = GPT4All(
                    model_name=MODEL_NAME,
                    model_path=ModelManager.get_model_path(),
                    allow_download=False, # We handle download manually now
                    device="cpu" # explicit fallback
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
                if not ModelManager.is_model_installed():
                     return "Error: Local AI Model not installed. Please go to Settings to download it."
                
                # Try lazy load if installed but not loaded
                self.__init__()
                if LocalAIEngine._model is None:
                    return "Error: Failed to load AI Model. Check logs."

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
