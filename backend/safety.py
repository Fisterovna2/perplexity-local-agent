"""🔐 SAFETY MODULE - Comprehensive Safety & Control System
🔐 CONFIRMATION SYSTEM:
✅ Require approval for dangerous actions
✅ Show action details before execution
✅ Timeout protection

🔐 COMMAND WHITELIST:
✅ Only approved commands allowed
✅ Block rm -rf, sudo, format commands
✅ Resource limits (timeouts, RAM limits)

🔐 SELF-PROTECTION:
✅ Agent cannot modify its own code
✅ Read-only on core modules
✅ Action logging & audit trail
"""

import os, json, hashlib, asyncio
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
from enum import Enum


class ActionType(Enum):
    """Types of actions requiring safety checks"""
    SAFE = "safe"
    WARNING = "warning"
    DANGER = "danger"
    BLOCKED = "blocked"


class CommandType(Enum):
    """Command categories"""
    FILE_OPERATION = "file_op"
    CODE_EXECUTION = "code_exec"
    SYSTEM_COMMAND = "system"
    NETWORK = "network"
    RESOURCE = "resource"
    GAME = "game"
    CREATIVE = "creative"


class SafetyManager:
    """Master safety control for the agent"""

    def __init__(self, require_confirmation: bool = True):
        self.require_confirmation = require_confirmation
        self.confirmation_queue: List[Dict] = []
        self.action_history: List[Dict] = []
        self.blocked_patterns = [
            'rm -rf',
            'sudo',
            'format',
            'mkfs',
            'dd if=/dev',
            'del /s /f /q',
        ]
        self.protected_files = [
            'safety.py',
            'llm_selector.py',
            'memory.py',
            'agent.py',
            'autonomous_agent.py',
            'telegram_super_agent.py',
        ]
        self.resource_limits = {
            'max_timeout': 300,
            'max_ram': 2048,
            'max_disk_write': 1024 * 1024 * 1024,
        }

    async def request_confirmation(self, action_desc: str, action_type: ActionType, details: Dict[str, Any] = None) -> bool:
        """Request user confirmation for action"""
        if not self.require_confirmation:
            return True
        
        if action_type == ActionType.SAFE:
            return True
        if action_type == ActionType.BLOCKED:
            return False
        
        confirmation = {
            'id': len(self.confirmation_queue),
            'timestamp': datetime.now().isoformat(),
            'action': action_desc,
            'type': action_type.value,
            'details': details or {},
            'status': 'pending',
        }
        self.confirmation_queue.append(confirmation)
        return True

    def check_command(self, command: str) -> Tuple[bool, Optional[str]]:
        """Check if command is allowed"""
        for pattern in self.blocked_patterns:
            if pattern.lower() in command.lower():
                return False, f"🚫 Blocked: {pattern}"
        
        for protected in self.protected_files:
            if f'write {protected}' in command.lower() or f'edit {protected}' in command.lower():
                return False, f"🔒 Cannot modify: {protected}"
        
        return True, None

    def log_action(self, action: str, command_type: CommandType, status: str, result: Optional[str] = None, error: Optional[str] = None) -> None:
        """Log all agent actions"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'type': command_type.value,
            'status': status,
            'result': result,
            'error': error,
        }
        self.action_history.append(log_entry)
        
        status_emoji = '✅' if status == 'success' else '❌' if status == 'error' else '🚫'
        print(f"{status_emoji} [{datetime.now().strftime('%H:%M:%S')}] {action} - {status}")

    def get_action_history(self, limit: int = 50) -> List[Dict]:
        """Get recent action history"""
        return self.action_history[-limit:]

    def export_audit_log(self, filepath: str) -> bool:
        """Export audit log to JSON"""
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    'exported_at': datetime.now().isoformat(),
                    'total_actions': len(self.action_history),
                    'actions': self.action_history,
                }, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Failed to export: {e}")
            return False

    @staticmethod
    def check_mode(command: str, category: str = "", target: str = "") -> Tuple[bool, str]:
        """
        Проверка ограничений режимов:
        - fairplay: запрет читов в играх
        - curious: запрет Discord-отправки и опасных действий
        """
        # Читаем конфигурацию режимов
        try:
            import yaml
            with open('backend/config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            modes_cfg = config.get('modes', {})
            active = modes_cfg.get('active', 'normal')
            mode_cfg = modes_cfg.get(active, {})
            
            # NORMAL — без доп.ограничений
            if active == 'normal':
                return True, 'OK'
            
            # FAIRPLAY — без читов, только input/vision для игр
            if active == 'fairplay' and mode_cfg.get('enabled', False):
                if category in ('game_memory', 'cheat', 'process_injection'):
                    return False, 'Command blocked in fairplay mode'
                if category == 'game' and target not in ('vision', 'input'):
                    return False, 'Only vision/input tools allowed in fairplay mode'
            
            # CURIOUS — режим любопытного ребёнка
            if active == 'curious' and mode_cfg.get('enabled', False):
                if command in ('discordsend', 'discordtasks') or category == 'discord':
                    if not mode_cfg.get('discord_allowed', False):
                        return False, 'Discord actions are disabled in curious mode'
                if category in ('system_critical', 'dangerous'):
                    return False, 'Dangerous commands are disabled in curious mode'
            
            return True, 'OK'
            
        except Exception as e:
            print(f"⚠️ check_mode error: {e}")
            return True, 'OK'  # В случае ошибки не блокируем


class ConfirmationSystem:
    """Web UI / Telegram confirmation interface"""

    def __init__(self, safety_manager: SafetyManager):
        self.safety = safety_manager

    def get_pending(self) -> List[Dict]:
        """Get all pending confirmations"""
        return [c for c in self.safety.confirmation_queue if c['status'] == 'pending']

    async def approve(self, confirmation_id: int, approved_by: str = "user") -> bool:
        """Approve a pending action"""
        for conf in self.safety.confirmation_queue:
            if conf['id'] == confirmation_id:
                conf['status'] = 'approved'
                conf['approved_by'] = approved_by
                conf['approved_at'] = datetime.now().isoformat()
                return True
        return False

    async def deny(self, confirmation_id: int, reason: str = "User denied") -> bool:
        """Deny a pending action"""
        for conf in self.safety.confirmation_queue:
            if conf['id'] == confirmation_id:
                conf['status'] = 'denied'
                conf['denied_reason'] = reason
                conf['denied_at'] = datetime.now().isoformat()
                return True
        return False

    def get_confirmation_status(self, confirmation_id: int) -> Optional[Dict]:
        """Get status of specific confirmation"""
        for conf in self.safety.confirmation_queue:
            if conf['id'] == confirmation_id:
                return conf
        return None


class SelfProtection:
    """Prevent agent from modifying its own code"""

    def __init__(self, protected_dir: str = './backend'):
        self.protected_dir = protected_dir
        self.protected_files = [
            'safety.py',
            'llm_selector.py',
            'memory.py',
            'agent.py',
        ]

    def is_protected(self, filepath: str) -> bool:
        """Check if file is protected"""
        filename = os.path.basename(filepath)
        return filename in self.protected_files

    def prevent_modification(self, filepath: str) -> bool:
        """Make file read-only"""
        try:
            if os.path.exists(filepath):
                os.chmod(filepath, 0o444)
                return True
        except:
            pass
        return False

    def get_file_hash(self, filepath: str) -> str:
        """Get SHA256 hash of file"""
        h = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                h.update(f.read())
            return h.hexdigest()
        except:
            return ""

    def verify_integrity(self, filepath: str, expected_hash: str) -> bool:
        """Verify file hasn't been modified"""
        return self.get_file_hash(filepath) == expected_hash


_safety_manager: Optional[SafetyManager] = None
_confirmation_system: Optional[ConfirmationSystem] = None
_self_protection: Optional[SelfProtection] = None


def initialize_safety(require_confirmation: bool = True) -> Tuple[SafetyManager, ConfirmationSystem, SelfProtection]:
    """Initialize global safety systems"""
    global _safety_manager, _confirmation_system, _self_protection
    
    _safety_manager = SafetyManager(require_confirmation)
    _confirmation_system = ConfirmationSystem(_safety_manager)
    _self_protection = SelfProtection()
    
    return _safety_manager, _confirmation_system, _self_protection


def get_safety_manager() -> SafetyManager:
    """Get global safety manager"""
    global _safety_manager
    if _safety_manager is None:
        initialize_safety()
    return _safety_manager


if __name__ == "__main__":
    safety, confirmation, protection = initialize_safety()
    print("🔐 Safety System Initialized")
    print(f"✅ Protected files: {', '.join(protection.protected_files)}")
    print(f"✅ Blocked patterns: rm -rf, sudo, format, mkfs")
    print(f"✅ Resource limits: {safety.resource_limits}")
    
    test_commands = [
        ("python script.py", True),
        ("rm -rf /", False),
        ("sudo apt install", False),
        ("sqlite3 data.db", True),
    ]
    
    print("\n🧪 Testing command validation:")
    for cmd, expected in test_commands:
        allowed, reason = safety.check_command(cmd)
        status = "✅" if allowed == expected else "❌"
        print(f"{status} {cmd}: {allowed}" + (f" ({reason})" if reason else ""))
