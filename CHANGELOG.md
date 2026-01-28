# CHANGELOG - 2026-01-28
# v2.0.0

## Bug Fixes

### Process Termination Dialog Error
- **Issue**: `'Page' object has no attribute 'dialog'` when terminating processes
- **Fix**: Updated `app_shell.py` to use `page.overlay.append(dialog)` instead of deprecated `page.dialog` API
- **File**: `app/ui/app_shell.py`

### Cloud Chat Fallback
- **Issue**: Cloud AI always fell back to RAG even with valid API key
- **Fix**: Changed fallback logic to only trigger on actual API errors (checking for specific error messages)
- **File**: `app/ui/pages/ai_chat.py`

### Chat Enter Key Behavior  
- **Issue**: Enter key didn't send messages (either created newline or did nothing)
- **Fix**: 
  - Added `shift_enter=True` to TextField
  - Fixed async handler by assigning `on_submit = send_message` directly (not via lambda)
- **File**: `app/ui/pages/ai_chat.py`

## Summary
- Enter now sends messages
- Shift+Enter creates new lines
- Process termination dialog works correctly
- Cloud AI no longer incorrectly falls back to RAG
