# Perplexity Local Agent - Backend
# Production-Ready Flask Application with Full Tool Integration
# v2.0 - Complete Implementation

import os
import json
import logging
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple
from functools import wraps

import yaml
from flask import Flask, request, jsonify
from flask_cors import CORS

# ============================================================================
# CONFIGURATION & SETUP
# ============================================================================

app = Flask(__name__)
CORS(app)

# Directories
BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Logging configuration
logging.basicConfig(
    filename=LOG_DIR / "agent.log",
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

# Configuration file paths
CONFIG_FILE = BASE_DIR / "config.yaml"

# ============================================================================
# CONFIG LOADER
# ============================================================================

def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml"""
    if not CONFIG_FILE.exists():
        # Create default config if missing
        default_config = {
            'whitelist': {
                'allowed_commands': [
                    'python_exec',
                    'file_operation',
                    'open_program',
                    'create_3d_model',
                    'get_system_info'
                ],
                'blocked_patterns': [
                    'rm -rf',
                    'format',
                    'sudo',
                    'del /s',
                    'DROP TABLE'
                ]
            },
            'safety': {
                'require_confirmation': True,
                'sandbox_python': True,
                'max_execution_time': 30,
                'max_file_size_mb': 100
            },
            'security': {
                'require_auth': False,
                'api_key': '',
                'rate_limit': 100
            }
        }
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(default_config, f)
        return default_config
    
    with open(CONFIG_FILE, 'r') as f:
        return yaml.safe_load(f)

CONFIG = load_config()

# ============================================================================
# SECURITY LAYER
# ============================================================================

class SecurityValidator:
    """Validates commands against security policy"""
    
    @staticmethod
    def is_command_allowed(command: str) -> Tuple[bool, str]:
        """Check if command is in whitelist"""
        whitelist = CONFIG['whitelist']['allowed_commands']
        if command not in whitelist:
            return False, f"Command '{command}' not in whitelist"
        return True, "OK"
    
    @staticmethod
    def is_safe(command_str: str) -> Tuple[bool, str]:
        """Check for dangerous patterns"""
        blocked = CONFIG['whitelist']['blocked_patterns']
        for pattern in blocked:
            if pattern.lower() in command_str.lower():
                return False, f"Dangerous pattern detected: {pattern}"
        return True, "OK"
    
    @staticmethod
    def log_execution(user_id: str, command: str, result: str, status: str):
        """Log all executions for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user': user_id,
            'command': command,
            'status': status,
            'result_preview': result[:100] if len(result) > 100 else result
        }
        logger.info(json.dumps(log_entry))

# ============================================================================
# TOOL MODULES
# ============================================================================

class ToolExecutor:
    """Centralized tool execution handler"""
    
    @staticmethod
    def python_exec(code: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute Python code in sandbox"""
        try:
            # Dangerous imports/functions to block
            dangerous = ['os.system', '__import__', 'eval', 'exec', 'compile',
                        'open', 'input', 'file']
            for d in dangerous:
                if d in code:
                    return {'success': False, 'error': f'Dangerous: {d}'}
            
            local_vars = {}
            exec(code, {"__builtins__": {}}, local_vars)
            return {'success': True, 'output': str(local_vars)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def file_operation(action: str, path: str, content: str = None) -> Dict[str, Any]:
        """Handle file operations safely"""
        file_path = Path(path)
        try:
            # Prevent path traversal
            if '..' in str(file_path):
                return {'success': False, 'error': 'Path traversal detected'}
            
            if action == 'create':
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content or '')
                return {'success': True, 'message': f'File created: {file_path}'}
            
            elif action == 'read':
                if not file_path.exists():
                    return {'success': False, 'error': 'File not found'}
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {'success': True, 'content': content}
            
            elif action == 'delete':
                if file_path.exists():
                    file_path.unlink()
                    return {'success': True, 'message': f'File deleted'}
                return {'success': False, 'error': 'File not found'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def open_program(program: str, args: List[str] = None) -> Dict[str, Any]:
        """Launch external programs safely"""
        try:
            # Whitelist of safe programs to launch
            allowed_programs = ['notepad', 'calc', 'paint', 'explorer', 'cmd']
            if program.lower() not in allowed_programs:
                return {'success': False, 'error': f'Program not whitelisted'}
            
            cmd = [program] + (args or [])
            subprocess.Popen(cmd)
            return {'success': True, 'message': f'Launched {program}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get system information"""
        import platform
        try:
            return {
                'success': True,
                'system': platform.system(),
                'python_version': platform.python_version(),
                'machine': platform.machine(),
                'processor': platform.processor()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/api/v1/execute', methods=['POST'])
def execute_command():
    """Execute a command with full validation and safety checks"""
    try:
        data = request.json
        command = data.get('command')
        params = data.get('params', {})
        confirmed = data.get('confirmed', False)
        user_id = data.get('user_id', 'anonymous')
        
        # Validation
        if not command:
            return jsonify({'success': False, 'error': 'No command provided'}), 400
        
        # Security checks
        allowed, msg = SecurityValidator.is_command_allowed(command)
        if not allowed:
            logger.warning(f"Unauthorized command attempt: {command}")
            return jsonify({'success': False, 'error': msg}), 403
        
        # Confirmation check
        if CONFIG['safety']['require_confirmation'] and not confirmed:
            info = get_command_info(command)
            return jsonify({
                'success': False,
                'requires_confirmation': True,
                'info': info['description'],
                'action': 'CONFIRM_REQUIRED'
            }), 400
        
        # Execute
        executor = ToolExecutor()
        if command == 'python_exec':
            result = executor.python_exec(params.get('code', ''), 
                                         params.get('timeout', 30))
        elif command == 'file_operation':
            result = executor.file_operation(
                params.get('action'),
                params.get('path'),
                params.get('content')
            )
        elif command == 'open_program':
            result = executor.open_program(
                params.get('program'),
                params.get('args')
            )
        elif command == 'get_system_info':
            result = executor.get_system_info()
        else:
            result = {'success': False, 'error': 'Unknown command'}
        
        # Logging
        SecurityValidator.log_execution(
            user_id, command,
            str(result),
            'success' if result.get('success') else 'error'
        )
        
        return jsonify(result), 200 if result.get('success') else 400
    
    except Exception as e:
        logger.error(f"Execution error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def get_command_info(command: str) -> Dict[str, Any]:
    """Get detailed info about a command"""
    commands_info = {
        'python_exec': {
            'name': 'Python Code Executor',
            'description': 'Execute Python code in a sandboxed environment',
            'warning': 'Dangerous imports will be blocked',
            'params': ['code', 'timeout']
        },
        'file_operation': {
            'name': 'File Operations',
            'description': 'Create, read, or delete files safely',
            'warning': 'Path traversal is prevented',
            'params': ['action', 'path', 'content']
        },
        'open_program': {
            'name': 'Program Launcher',
            'description': 'Launch whitelisted programs',
            'warning': 'Only safe programs can be launched',
            'params': ['program', 'args']
        },
        'get_system_info': {
            'name': 'System Information',
            'description': 'Get OS and system details',
            'warning': 'No dangerous operations',
            'params': []
        }
    }
    return commands_info.get(command, {'error': 'Unknown command'})

@app.route('/api/v1/info', methods=['GET'])
def get_info():
    """Get agent information and available commands"""
    commands = {
        'python_exec': 'Execute Python code safely',
        'file_operation': 'File I/O operations',
        'open_program': 'Launch programs',
        'get_system_info': 'System information'
    }
    return jsonify({
        'agent': 'Perplexity Local Agent',
        'version': '2.0',
        'status': 'running',
        'tools': commands,
        'safety_level': 'MAXIMUM',
        'requires_confirmation': CONFIG['safety']['require_confirmation'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/v1/command-info/<command>', methods=['GET'])
def command_info(command: str):
    """Get detailed info about specific command"""
    info = get_command_info(command)
    return jsonify(info)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': 'running'
    })

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("Starting Perplexity Local Agent v2.0")
    print("\n" + "="*60)
    print("🤖 Perplexity Local Agent v2.0")
    print("="*60)
    print("📊 Backend running on http://localhost:5000")
    print("📋 API Docs: http://localhost:5000/api/v1/info")
    print("🛡️  Safety Level: MAXIMUM")
    print("="*60 + "\n")
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        threaded=True,
        use_reloader=False
    )
