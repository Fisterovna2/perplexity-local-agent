# Perplexity Local Agent - Backend
# Flask REST API for executing commands on local PC

import os
import json
import logging
import subprocess
import yaml
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Logging setup
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "agent.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Config
CONFIG_FILE = "config.yaml"
WHITELIST = {}
BLACKLIST = {"taskkill", "format", "del /s /q", "rd /s /q", "cipher"}

def load_config():
    """Load whitelist from config"""
    global WHITELIST
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = yaml.safe_load(f) or {}
            WHITELIST = config.get('allowed_commands', {})

def is_command_allowed(action, command):
    """Check if command is whitelisted"""
    if action not in WHITELIST:
        return False, f"Action '{action}' not allowed"
    
    for banned in BLACKLIST:
        if banned.lower() in command.lower():
            return False, f"Dangerous command detected: {banned}"
    
    return True, "OK"

def log_action(action, command, status, user_ip):
    """Log all actions"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "command": command[:100],
        "status": status,
        "user_ip": user_ip
    }
    logger.info(json.dumps(log_entry))

# ENDPOINTS
@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"status": "online", "version": "1.0.0"})

@app.route('/api/validate', methods=['POST'])
def validate():
    """Validate command before execution"""
    data = request.json
    action = data.get('action')
    command = data.get('command')
    
    allowed, reason = is_command_allowed(action, command)
    return jsonify({"allowed": allowed, "reason": reason})

@app.route('/api/execute', methods=['POST'])
def execute():
    """Execute validated command"""
    data = request.json
    action = data.get('action')
    command = data.get('command')
    confirmed = data.get('confirmed', False)
    user_ip = request.remote_addr
    
    if not confirmed:
        return jsonify({"success": False, "error": "Not confirmed"}), 403
    
    allowed, reason = is_command_allowed(action, command)
    if not allowed:
        log_action(action, command, f"DENIED: {reason}", user_ip)
        return jsonify({"success": False, "error": reason}), 403
    
    try:
        result = {"message": "Executed"}
        log_action(action, command, "SUCCESS", user_ip)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        log_action(action, command, f"ERROR: {str(e)}", user_ip)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/info', methods=['POST'])
def get_info():
    """Get action info"""
    data = request.json
    action = data.get('action')
    
    descriptions = {
        "blender_script": "Run Python script in Blender (headless)",
        "python_script": "Run arbitrary Python code on PC",
        "file_operation": "File create/read/write operations",
        "open_program": "Open programs or files"
    }
    
    return jsonify({
        "action": action,
        "description": descriptions.get(action, "Unknown"),
        "risks": ["Uses PC resources", "Creates files", "Runs programs"]
    })

if __name__ == '__main__':
    load_config()
    print("🚀 Perplexity Local Agent running on http://localhost:5000")
    app.run(host='127.0.0.1', port=5000, debug=False)
