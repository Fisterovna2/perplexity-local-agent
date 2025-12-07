# CRITICAL BUG FIX - API Endpoints

## Problem
The agent backend starts successfully but ALL API endpoints (/api/v1/info, /api/v1/task) return "Internal server error" (500).

## Root Cause
Line 323 in `backend/agent.py` tries to access `CONFIG['safety']['require_confirmation']` but the CONFIG dictionary doesn't have a 'safety' key, causing a KeyError that crashes the route handler.

## Quick Fix

Open `backend/agent.py` and find line 323:
```python
'require_confirmation': CONFIG['safety']['require_confirmation'],
```

Replace it with:
```python
'require_confirmation': CONFIG.get('safety', {}).get('require_confirmation', True),
```

This safely checks for the key and defaults to True if missing.

## Complete Fix Instructions

1. **Stop the running agent** (Ctrl+C in terminal)

2. **Edit backend/agent.py:**
   - Find line 323: `'require_confirmation': CONFIG['safety']['require_confirmation'],`
   - Replace with: `'require_confirmation': CONFIG.get('safety', {}).get('require_confirmation', True),`

3. **Restart the agent:**
   ```bash
   cd backend
   python agent.py
   ```

4. **Test the API:**
   ```bash
   curl http://localhost:5000/api/v1/info
   ```

You should now see JSON response instead of "Internal server error".

## Status
✅ Backend launches successfully
❌ API endpoints crash due to missing CONFIG keys
🔧 Fix: Use .get() with defaults for all CONFIG access

## Next Steps
After applying this fix:
- Test /api/v1/info endpoint
- Implement /api/v1/task POST endpoint
- Integrate safety modules (VirusTotal, confirmation_system, self_protection)
- Complete frontend integration
