"""Flask Web UI for Perplexity Local Agent"""
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import sys
import os
import json
import logging
from datetime import datetime
import io
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from llm_selector import llm_selector
    from planner import planner
    from input_control import input_controller
    from vision_controller import vision
    from safety import safety_manager
    from memory import memory
except ImportError as e:
    print(f"Warning: Could not import backend modules: {e}")

app = Flask(__name__, template_folder='.', static_folder='.')
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentState:
    def __init__(self):
        self.current_model = "gpt-4o"
        self.is_running = False
        self.current_task = None
        self.command_history = []
        self.plan = None
        self.status = "idle"
        self.last_screenshot = None
        self.approvals_pending = []
        
    def to_dict(self):
        return {
            "current_model": self.current_model,
            "is_running": self.is_running,
            "current_task": self.current_task,
            "status": self.status,
            "plan": self.plan,
            "command_history": self.command_history[-50:],
            "approvals_pending": self.approvals_pending
        }

agent_state = AgentState()

@app.route('/')
def index():
    """Serve main dashboard"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get current agent status"""
    return jsonify(agent_state.to_dict())

@app.route('/api/models')
def get_models():
    """Get available LLM models"""
    models = [
        {"id": "gpt-4o", "name": "GPT-4o", "provider": "OpenAI"},
        {"id": "claude-3.5", "name": "Claude 3.5 Sonnet", "provider": "Anthropic"},
        {"id": "gemini-pro", "name": "Gemini Pro", "provider": "Google"},
        {"id": "llama-3", "name": "Llama 3", "provider": "Meta"},
        {"id": "perplexity", "name": "Perplexity", "provider": "Perplexity"},
        {"id": "custom", "name": "Custom API", "provider": "Custom"}
    ]
    return jsonify(models)

@app.route('/api/model/select', methods=['POST'])
def select_model():
    """Select LLM model"""
    data = request.json
    model_id = data.get('model_id')
    agent_state.current_model = model_id
    logger.info(f"Model selected: {model_id}")
    return jsonify({"success": True, "model": model_id})

@app.route('/api/screenshot')
def get_screenshot():
    """Get current screen screenshot"""
    try:
        frame = vision.capture_screen()
        base64_img = vision.get_screenshot_base64()
        agent_state.last_screenshot = base64_img
        return jsonify({"screenshot": base64_img, "timestamp": datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze')
def analyze_screenshot():
    """Analyze current screenshot"""
    try:
        analysis = vision.analyze_full_screenshot()
        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/command', methods=['POST'])
def execute_command():
    """Execute command with approval"""
    data = request.json
    command = data.get('command')
    
    agent_state.command_history.append({
        "timestamp": datetime.now().isoformat(),
        "command": command,
        "status": "pending_approval"
    })
    
    agent_state.approvals_pending.append({
        "id": len(agent_state.approvals_pending),
        "command": command,
        "timestamp": datetime.now().isoformat()
    })
    
    logger.info(f"Command pending approval: {command}")
    return jsonify({"success": True, "command": command})

@app.route('/api/approve', methods=['POST'])
def approve_command():
    """Approve pending command"""
    data = request.json
    approval_id = data.get('id')
    
    for approval in agent_state.approvals_pending:
        if approval['id'] == approval_id:
            command = approval['command']
            agent_state.approvals_pending.remove(approval)
            
            try:
                # Execute command (simplified)
                logger.info(f"Executing command: {command}")
                result = {"success": True, "output": f"Executed: {command}"}
            except Exception as e:
                result = {"success": False, "error": str(e)}
            
            return jsonify(result)
    
    return jsonify({"error": "Approval not found"}), 404

@app.route('/api/deny', methods=['POST'])
def deny_command():
    """Deny pending command"""
    data = request.json
    approval_id = data.get('id')
    
    for approval in agent_state.approvals_pending:
        if approval['id'] == approval_id:
            agent_state.approvals_pending.remove(approval)
            logger.info(f"Command denied: {approval['command']}")
            return jsonify({"success": True})
    
    return jsonify({"error": "Approval not found"}), 404

@app.route('/api/plan', methods=['POST'])
def create_plan():
    """Create execution plan from task"""
    data = request.json
    task = data.get('task')
    
    agent_state.current_task = task
    agent_state.status = "planning"
    
    try:
        plan_steps = [
            {"step": 1, "action": "Analyze task", "status": "pending"},
            {"step": 2, "action": "Break into subtasks", "status": "pending"},
            {"step": 3, "action": "Execute plan", "status": "pending"}
        ]
        agent_state.plan = plan_steps
        logger.info(f"Plan created for task: {task}")
        return jsonify({"success": True, "plan": plan_steps})
    except Exception as e:
        logger.error(f"Plan error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/execute', methods=['POST'])
def execute_plan():
    """Execute current plan"""
    agent_state.status = "executing"
    agent_state.is_running = True
    
    try:
        logger.info(f"Executing plan for task: {agent_state.current_task}")
        return jsonify({"success": True, "status": "executing"})
    except Exception as e:
        agent_state.is_running = False
        logger.error(f"Execution error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/cancel', methods=['POST'])
def cancel_execution():
    """Cancel current execution"""
    agent_state.is_running = False
    agent_state.status = "idle"
    agent_state.current_task = None
    agent_state.plan = None
    logger.info("Execution cancelled")
    return jsonify({"success": True, "status": "idle"})

@app.route('/api/memory')
def get_memory():
    """Get agent memory/history"""
    return jsonify({"command_history": agent_state.command_history[-100:]})

@app.route('/api/logs')
def get_logs():
    """Get application logs"""
    return jsonify({"logs": agent_state.command_history[-50:]})

if __name__ == '__main__':
    logger.info("Starting Perplexity Local Agent Web UI")
    logger.info("Open http://localhost:5000 in your browser")
    app.run(host='0.0.0.0', port=5000, debug=False)
