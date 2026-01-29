import asyncio
import flet as ft
from app.intelligence.local_ai import LocalAIEngine
from app.intelligence.cloud_ai import CloudAIEngine
from app.ai.model_manager import ModelManager
import json
import os

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"ai_mode": "rag", "api_key": ""}  # Default to RAG


def view(ai_context=None):
    config = load_config()
    
    # Initialize all engines
    from app.intelligence.rag_engine import RAGEngine
    from app.storage.chat_history import ChatHistory
    
    rag_engine = RAGEngine()
    local_engine = LocalAIEngine()
    cloud_engine = CloudAIEngine(api_key=config.get('api_key', ''))
    chat_history = ChatHistory()
    
    # Determine primary mode
    mode = config.get('ai_mode', 'rag')
    
    # Check if local model is actually installed
    if mode == "local" and not ModelManager.is_model_installed():
        mode_text = "Local (Model Missing)"
    else:
        mode_text = {"rag": "RAG", "local": "Local", "cloud": "Cloud"}.get(mode, "RAG")
    
    messages = ft.Column(expand=True, spacing=10, scroll=ft.ScrollMode.AUTO)
    
    # Loading indicator
    loading_indicator = ft.ProgressRing(visible=False, width=20, height=20)
    
    input_box = ft.TextField(
        hint_text=f"Message SysSentinel ({mode_text})…",
        expand=True,
        multiline=True,
        min_lines=1,
        max_lines=5,
        shift_enter=True,  # Enter sends, Shift+Enter for new line
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=ft.Colors.TRANSPARENT,
        on_submit=None,  # Will be set after send_message is defined
    )

    def add_message(text, sender="user", save_to_history=True):
        # User: Blue tint, AI: Purple tint
        bg_color = ft.Colors.BLUE_900 if sender == "user" else ft.Colors.PURPLE_900
        align = ft.MainAxisAlignment.END if sender == "user" else ft.MainAxisAlignment.START
        
        # Check for commands in the text (simple regex for taskkill)
        command_to_run = None
        if sender == "ai":
            import re
            # Improved regex to catch commands in backticks or code blocks
            # Catches: `taskkill ...` or ```taskkill ...```
            # Also handles multi-line blocks where taskkill starts the line
            match = re.search(r'[`\s]*(taskkill\s+.*?)(?:`|\n|$)', text, re.IGNORECASE | re.DOTALL)
            
            if match:
                raw_cmd = match.group(1).strip()
                # Clean up any potential markdown residue or placeholders
                if "<" not in raw_cmd and ">" not in raw_cmd:
                    command_to_run = raw_cmd

        msg_content = ft.Column([
            ft.Text(text, selectable=True, color=ft.Colors.WHITE, size=14)
        ])
        
        if command_to_run:
            def run_cmd(cmd):
                import subprocess
                try:
                    subprocess.run(cmd, shell=True, check=True)
                    add_message(f"✅ Executed: `{cmd}`", sender="ai", save_to_history=False)
                except Exception as e:
                    add_message(f"❌ Failed: {e}", sender="ai", save_to_history=False)
                messages.update()

            msg_content.controls.append(
                ft.Container(
                    content=ft.ElevatedButton(
                        "Run Code", 
                        icon=ft.Icons.PLAY_ARROW, 
                        bgcolor=ft.Colors.GREEN_700,
                        color=ft.Colors.WHITE,
                        on_click=lambda e, c=command_to_run: run_cmd(c)
                    ),
                    padding=ft.padding.only(top=10)
                )
            )

        messages.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=msg_content,
                        padding=15,
                        border_radius=15,
                        bgcolor=bg_color,
                        opacity=0.9,
                        width=600,
                    )
                ],
                alignment=align,
            )
        )
        
        # Save to persistent storage if new message
        if save_to_history:
            chat_history.add_message(text, sender)
            
    # Load previous messages from history
    for msg in chat_history.get_messages():
        add_message(msg["text"], msg["sender"], save_to_history=False)

    # Build fresh context immediately
    # Build fresh context immediately
    from app.intelligence.context_builder import ContextBuilder
    
    # Safe payload access
    payload = ai_context.get("payload") or {} if ai_context else {}
    
    context_text = ContextBuilder.build_combined_context(
        pid=payload.get("pid"),
        name=payload.get("name"),
        cpu=payload.get("cpu_percent"),
        mem=payload.get("memory_mb")
    )
    
    # Send initial greeting if context loaded (and not already in history)
    if ai_context and ai_context.get("payload"):
        # This is a specific process context
        add_message(
            f"✓ Process context loaded for **{ai_context['payload']['name']}**. I can answer specific questions about its resource usage.",
            sender="ai",
            save_to_history=False
        )

    async def send_message(e):
        user_text = input_box.value.strip()
        if not user_text:
            return

        # 1. Clear input and show loading UI immediately
        input_box.value = ""
        input_box.disabled = True
        loading_indicator.visible = True
        
        # 2. Add user message
        add_message(user_text, sender="user")
        
        # 3. Async update to ensure UI renders BEFORE AI starts
        messages.update()
        input_box.update()
        loading_indicator.update()
        
        # Refresh context logic
        refresh_payload = ai_context.get("payload") or {} if ai_context else {}
        
        # NOTE: ContextBuilder might be sync, but it's fast. 
        # If it does heavy I/O, it should also be threaded, but regex is fine.
        from app.intelligence.context_builder import ContextBuilder
        fresh_context_text = ContextBuilder.build_combined_context(
            pid=refresh_payload.get("pid"),
            name=refresh_payload.get("name")
        )

        enhanced_prompt = user_text
        if fresh_context_text:
            enhanced_prompt = f"""YOU ARE A SYSTEM MONITORING ASSISTANT. I am providing you with REAL, LIVE system data below.
CRITICAL INSTRUCTIONS:
1. Answer ONLY using the specific data provided below
2. Give DIRECT answers with specific numbers, names, and values from the data
3. If asked to terminate/kill:
   - Priority 1: Instruct to use the UI (Performance tab -> ⋮ menu)
   - Priority 2: If USER SPECIFICALLY ASKS for a command:
     - Use PID if known: `taskkill /F /PID <pid>`
     - If PID unknown: `taskkill /F /IM process_name.exe` (replace 'process_name' with the actual name, e.g., chrome.exe)
4. If a process isn't listed, you can still give the generic name-based command.

===== LIVE SYSTEM DATA =====
{fresh_context_text}
===== END OF DATA =====

USER QUESTION: {user_text}

Answer using the data above. If user asks for a command, provide it used specific real names, DO NOT use placeholders like <name>."""

        # Define the AI generation task
        def generate_response():
             # Reload config to get current mode
            current_config = load_config()
            current_mode = current_config.get('ai_mode', 'rag')
            used_mode = {"rag": "RAG", "local": "Local", "cloud": "Cloud"}.get(current_mode, "RAG")
            
            ai_resp = None
            should_fallback = False
            try:
                if current_mode == "rag":
                    rag_engine.set_context(fresh_context_text if fresh_context_text else context_text)
                    ai_resp = rag_engine.generate(user_text)
                elif current_mode == "local":
                    if not ModelManager.is_model_installed():
                        ai_resp = "⚠️ Local Model not found. Please go to Settings > AI Capabilities to download it."
                        used_mode = "System"
                        should_fallback = True
                    else:
                        ai_resp = local_engine.generate(enhanced_prompt, "")
                elif current_mode == "cloud":
                    current_cloud_engine = CloudAIEngine(api_key=current_config.get('api_key', ''))
                    ai_resp = current_cloud_engine.generate(enhanced_prompt, "")
                    # Only fallback on actual API errors (these start with ⚠️ and contain specific error messages)
                    if ai_resp and ai_resp.startswith("⚠️") and ("Error" in ai_resp or "No API key" in ai_resp or "Invalid API key" in ai_resp or "timed out" in ai_resp):
                        should_fallback = True
                
            except Exception as e:
                should_fallback = True
            
            # Fallback to RAG if primary mode failed
            if should_fallback:
                try:
                    rag_engine.set_context(fresh_context_text if fresh_context_text else context_text)
                    ai_resp = rag_engine.generate(user_text)
                    used_mode = "RAG (fallback)"
                except:
                    ai_resp = "⚠️ All AI systems failed. Please try again later."
                    used_mode = "Error"
            
            return f"[{used_mode}] {ai_resp}"

        # Run AI in thread to avoid blocking UI
        final_response = await asyncio.to_thread(generate_response)
        
        loading_indicator.visible = False
        input_box.disabled = False
        add_message(final_response, sender="ai")
        messages.update()
        input_box.update()
        loading_indicator.update()
    
    def clear_chat(e):
        """Clear all chat messages."""
        messages.controls.clear()
        chat_history.clear_history()
        messages.update()

    # Set the on_submit handler after send_message is defined
    input_box.on_submit = send_message
    return ft.Column(
        [
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Text(f"AI Assistant ({mode_text})", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_SWEEP,
                        tooltip="Clear chat history",
                        on_click=lambda e: clear_chat(e)
                    ),
                    ft.Icon(
                        ft.Icons.CLOUD if config['ai_mode'] == 'cloud' else ft.Icons.COMPUTER,
                        color=ft.Colors.BLUE_400,
                        size=24
                    )
                ]),
                padding=ft.padding.only(left=20, right=20, top=15, bottom=10),
            ),
            ft.Divider(height=1),
            
            # Messages Area
            ft.Container(
                content=messages,
                expand=True,
                padding=20,
            ),
            
            # Input Area (ChatGPT Style)
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            input_box,
                            loading_indicator,
                            ft.IconButton(
                                icon=ft.Icons.ARROW_UPWARD,
                                on_click=send_message,
                                bgcolor=ft.Colors.BLUE_700,
                                icon_color=ft.Colors.WHITE,
                                icon_size=20,
                            ),
                        ], spacing=10),
                        padding=15,
                        bgcolor=ft.Colors.BLUE_GREY_900,
                        border_radius=25,
                        border=ft.border.all(1, ft.Colors.BLUE_GREY_700),
                    ),
                    ft.Text(
                        "SysSentinel can make mistakes. Check important info.",
                        size=11,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER
                    ),
                ], spacing=8),
                padding=ft.padding.only(left=20, right=20, bottom=15),
            ),
        ],
        expand=True,
        spacing=0,
    )
