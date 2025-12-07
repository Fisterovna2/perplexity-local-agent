#!/usr/bin/env python3
"""
User Confirmation System - Requires explicit user approval before PC actions
Перед каждым действием на ПК запрашивает разрешение пользователя
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import threading
import queue

logger = logging.getLogger(__name__)

class ActionType:
    """Categories of actions requiring confirmation"""
    FILE_OPERATION = "file_operation"
    PROGRAM_EXECUTION = "program_execution"
    SYSTEM_COMMAND = "system_command"
    NETWORK_ACCESS = "network_access"
    DOWNLOAD_FILE = "download_file"
    GAME_INTERACTION = "game_interaction"
    SCREEN_CONTROL = "screen_control"
    KEYBOARD_INPUT = "keyboard_input"
    MOUSE_CONTROL = "mouse_control"

class ConfirmationRequest:
    """Represents a confirmation request with detailed information"""
    
    def __init__(self, action_type: str, description: str, details: Dict[str, Any]):
        self.id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.action_type = action_type
        self.description = description
        self.details = details
        self.timestamp = datetime.now().isoformat()
        self.status = "pending"  # pending, approved, denied
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action_type": self.action_type,
            "description": self.description,
            "details": self.details,
            "timestamp": self.timestamp,
            "status": self.status
        }

class ConfirmationSystem:
    """
    Manages user confirmations for all PC actions
    Shows INFO button with detailed action description
    """
    
    def __init__(self):
        self.pending_requests: Dict[str, ConfirmationRequest] = {}
        self.confirmation_history: List[ConfirmationRequest] = []
        self.response_queue = queue.Queue()
        self.auto_deny_dangerous = True  # Auto-deny clearly dangerous operations
        
        # Actions that are always dangerous and require extra confirmation
        self.critical_actions = [
            "delete_system_file",
            "modify_registry",
            "disable_security",
            "execute_untrusted_code"
        ]
        
        logger.info("✅ Confirmation System initialized")
    
    def request_confirmation(self, 
                           action_type: str, 
                           description: str, 
                           details: Dict[str, Any],
                           timeout: int = 60) -> bool:
        """
        Request user confirmation for an action
        
        Args:
            action_type: Type of action (from ActionType class)
            description: Human-readable description
            details: Detailed information about the action
            timeout: Timeout in seconds
        
        Returns:
            bool: True if approved, False if denied
        """
        # Check if action is critical
        if self._is_critical_action(details):
            logger.warning(f"🚨 CRITICAL ACTION detected: {description}")
            description = f"⚠️ КРИТИЧЕСКОЕ ДЕЙСТВИЕ: {description}"
        
        request = ConfirmationRequest(action_type, description, details)
        self.pending_requests[request.id] = request
        
        logger.info(f"📋 Confirmation requested: {description}")
        logger.info(f"   Details: {json.dumps(details, indent=2)}")
        
        # Send request to frontend
        self._send_confirmation_request(request)
        
        # Wait for response
        try:
            response = self.response_queue.get(timeout=timeout)
            
            if response.get("request_id") == request.id:
                approved = response.get("approved", False)
                request.status = "approved" if approved else "denied"
                
                self.confirmation_history.append(request)
                del self.pending_requests[request.id]
                
                if approved:
                    logger.info(f"✅ Action APPROVED: {description}")
                else:
                    logger.warning(f"❌ Action DENIED: {description}")
                
                return approved
        
        except queue.Empty:
            logger.warning(f"⏰ Confirmation timeout for: {description}")
            request.status = "timeout"
            self.confirmation_history.append(request)
            del self.pending_requests[request.id]
            return False
    
    def _is_critical_action(self, details: Dict[str, Any]) -> bool:
        """Check if action is critical/dangerous"""
        # Check for dangerous keywords
        details_str = json.dumps(details).lower()
        
        dangerous_keywords = [
            "system32", "registry", "admin", "root",
            "delete", "format", "rmdir", "rm -rf",
            "sudo", "powershell", "cmd.exe"
        ]
        
        return any(keyword in details_str for keyword in dangerous_keywords)
    
    def _send_confirmation_request(self, request: ConfirmationRequest):
        """
        Send confirmation request to frontend UI
        This will display:
        - Dialog with action description
        - INFO button showing detailed information
        - APPROVE / DENY buttons
        """
        # This would send to Flask frontend via WebSocket/REST API
        request_data = request.to_dict()
        
        # Add formatted info for display
        request_data["formatted_details"] = self._format_details_for_display(request.details)
        
        # TODO: Send to frontend via API
        # In real implementation, this would use Flask-SocketIO or REST endpoint
        logger.debug(f"Sending confirmation request to frontend: {request_data}")
    
    def _format_details_for_display(self, details: Dict[str, Any]) -> str:
        """Format details for user-friendly display"""
        formatted = []
        
        for key, value in details.items():
            # Make keys human-readable
            readable_key = key.replace("_", " ").title()
            formatted.append(f"{readable_key}: {value}")
        
        return "\n".join(formatted)
    
    def submit_response(self, request_id: str, approved: bool):
        """Submit user response to pending confirmation"""
        self.response_queue.put({
            "request_id": request_id,
            "approved": approved
        })
    
    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Get all pending confirmation requests"""
        return [req.to_dict() for req in self.pending_requests.values()]
    
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get confirmation history"""
        return [req.to_dict() for req in self.confirmation_history[-limit:]]

# Example usage functions for different action types

def confirm_file_operation(confirmation_system: ConfirmationSystem, 
                          operation: str, 
                          file_path: str) -> bool:
    """Confirm file operation"""
    return confirmation_system.request_confirmation(
        action_type=ActionType.FILE_OPERATION,
        description=f"Выполнить операцию с файлом: {operation}",
        details={
            "operation": operation,
            "file_path": file_path,
            "risk_level": "medium"
        }
    )

def confirm_program_execution(confirmation_system: ConfirmationSystem,
                            program_path: str,
                            arguments: List[str]) -> bool:
    """Confirm program execution"""
    return confirmation_system.request_confirmation(
        action_type=ActionType.PROGRAM_EXECUTION,
        description=f"Запустить программу: {program_path}",
        details={
            "program": program_path,
            "arguments": arguments,
            "risk_level": "high"
        }
    )

def confirm_game_action(confirmation_system: ConfirmationSystem,
                       game_name: str,
                       action: str) -> bool:
    """Confirm game interaction (e.g., Roblox)"""
    return confirmation_system.request_confirmation(
        action_type=ActionType.GAME_INTERACTION,
        description=f"Выполнить действие в игре {game_name}: {action}",
        details={
            "game": game_name,
            "action": action,
            "risk_level": "low"
        }
    )

def confirm_download(confirmation_system: ConfirmationSystem,
                    url: str,
                    file_name: str,
                    file_size: int) -> bool:
    """Confirm file download"""
    return confirmation_system.request_confirmation(
        action_type=ActionType.DOWNLOAD_FILE,
        description=f"Скачать файл: {file_name}",
        details={
            "url": url,
            "file_name": file_name,
            "file_size_mb": round(file_size / (1024*1024), 2),
            "risk_level": "medium"
        }
    )

if __name__ == "__main__":
    # Test the confirmation system
    logging.basicConfig(level=logging.INFO)
    
    system = ConfirmationSystem()
    
    # Simulate confirmation request
    print("Testing confirmation system...")
    
    # This would normally wait for UI response
    # For testing, we'll just create a request
    system.request_confirmation(
        action_type=ActionType.FILE_OPERATION,
        description="Create test file",
        details={"path": "/test/file.txt", "operation": "create"}
    )
