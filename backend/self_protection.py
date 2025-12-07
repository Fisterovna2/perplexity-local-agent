#!/usr/bin/env python3
"""
Self-Protection Module - Prevents agent from modifying its own code
Модуль самозащиты - предотвращает редактирование агентом собственного кода
"""

import os
import sys
import logging
from pathlib import Path
from typing import Set, List, Optional
import hashlib
import json

logger = logging.getLogger(__name__)

class SelfProtection:
    """
    Protects the agent from modifying its own code files
    Blocks any file operations that target the backend/ directory
    """
    
    def __init__(self, project_root: Optional[str] = None):
        if project_root is None:
            # Auto-detect project root
            project_root = self._find_project_root()
        
        self.project_root = Path(project_root).resolve()
        self.backend_dir = self.project_root / "backend"
        self.protected_files: Set[Path] = set()
        self.file_hashes: dict = {}  # Track file integrity
        
        # Critical files that must never be modified
        self.critical_files = [
            "agent.py",
            "self_protection.py",
            "confirmation_system.py",
            "internet_safety.py",
            "config.yaml"
        ]
        
        self._scan_protected_files()
        self._compute_file_hashes()
        
        logger.info(f"🛡️ Self-Protection initialized")
        logger.info(f"   Protected directory: {self.backend_dir}")
        logger.info(f"   Protected files: {len(self.protected_files)}")
    
    def _find_project_root(self) -> str:
        """Find the project root directory"""
        current = Path(__file__).parent
        
        # Go up until we find the project root (contains backend/ and frontend/)
        while current != current.parent:
            if (current / "backend").exists() and (current / "frontend").exists():
                return str(current)
            current = current.parent
        
        # If not found, use current file's parent directory
        return str(Path(__file__).parent)
    
    def _scan_protected_files(self):
        """Scan and register all files in backend directory"""
        if not self.backend_dir.exists():
            logger.warning(f"⚠️ Backend directory not found: {self.backend_dir}")
            return
        
        for file_path in self.backend_dir.rglob("*.py"):
            self.protected_files.add(file_path.resolve())
        
        # Also protect config files
        for config_file in ["config.yaml", "requirements.txt"]:
            config_path = self.backend_dir / config_file
            if config_path.exists():
                self.protected_files.add(config_path.resolve())
    
    def _compute_file_hashes(self):
        """Compute SHA256 hashes of all protected files for integrity checking"""
        for file_path in self.protected_files:
            try:
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                    self.file_hashes[str(file_path)] = file_hash
            except Exception as e:
                logger.error(f"❌ Error hashing {file_path}: {e}")
    
    def is_protected_path(self, path: str) -> bool:
        """
        Check if a given path is protected (within backend directory)
        
        Args:
            path: File path to check
        
        Returns:
            bool: True if path is protected
        """
        try:
            target_path = Path(path).resolve()
            
            # Check if path is in protected files
            if target_path in self.protected_files:
                return True
            
            # Check if path is within backend directory
            try:
                target_path.relative_to(self.backend_dir)
                return True
            except ValueError:
                # Path is not relative to backend_dir
                pass
            
            return False
        
        except Exception as e:
            logger.error(f"❌ Error checking path {path}: {e}")
            # If in doubt, protect it
            return True
    
    def validate_operation(self, operation: str, path: str) -> tuple[bool, str]:
        """
        Validate if an operation on a path is allowed
        
        Args:
            operation: Operation type (read, write, delete, execute)
            path: Target file path
        
        Returns:
            tuple: (is_allowed, reason)
        """
        if not self.is_protected_path(path):
            return True, "Path not protected"
        
        target_path = Path(path).resolve()
        file_name = target_path.name
        
        # Read operations are always allowed
        if operation == "read":
            return True, "Read operation allowed"
        
        # Check if it's a critical file
        if file_name in self.critical_files:
            reason = f"❌ BLOCKED: Cannot {operation} critical file {file_name}"
            logger.warning(reason)
            return False, reason
        
        # Block write/delete operations on protected files
        if operation in ["write", "delete", "modify"]:
            reason = f"❌ BLOCKED: Cannot {operation} protected file in backend/ directory"
            logger.warning(reason)
            logger.warning(f"   Attempted operation: {operation}")
            logger.warning(f"   Target path: {path}")
            return False, reason
        
        # Execute operations might be allowed for non-critical files
        if operation == "execute":
            if file_name in self.critical_files:
                return False, f"❌ Cannot execute critical file {file_name}"
            return True, "Execute allowed for non-critical file"
        
        # Default: block unknown operations
        return False, f"❌ Unknown operation '{operation}' blocked"
    
    def check_file_integrity(self) -> List[str]:
        """
        Check if any protected files have been modified
        
        Returns:
            List of modified file paths
        """
        modified_files = []
        
        for file_path_str, original_hash in self.file_hashes.items():
            file_path = Path(file_path_str)
            
            if not file_path.exists():
                modified_files.append(f"{file_path} (DELETED)")
                logger.error(f"🚨 CRITICAL: Protected file deleted: {file_path}")
                continue
            
            try:
                with open(file_path, 'rb') as f:
                    current_hash = hashlib.sha256(f.read()).hexdigest()
                
                if current_hash != original_hash:
                    modified_files.append(str(file_path))
                    logger.warning(f"⚠️ File modified: {file_path}")
            
            except Exception as e:
                logger.error(f"❌ Error checking {file_path}: {e}")
        
        return modified_files
    
    def get_protected_files_list(self) -> List[str]:
        """Get list of all protected file paths"""
        return [str(p) for p in sorted(self.protected_files)]
    
    def is_safe_operation(self, operation: str, path: str) -> bool:
        """
        Quick check if operation is safe (convenience method)
        
        Args:
            operation: Operation type
            path: Target path
        
        Returns:
            bool: True if operation is safe
        """
        is_allowed, _ = self.validate_operation(operation, path)
        return is_allowed

# Decorator for protecting functions that perform file operations
def protect_file_operation(operation_type: str):
    """
    Decorator to protect file operations from modifying protected files
    
    Usage:
        @protect_file_operation("write")
        def write_file(path, content):
            ...
    """
    def decorator(func):
        def wrapper(path, *args, **kwargs):
            # Get or create self-protection instance
            if not hasattr(wrapper, '_protection'):
                wrapper._protection = SelfProtection()
            
            protection = wrapper._protection
            is_allowed, reason = protection.validate_operation(operation_type, path)
            
            if not is_allowed:
                raise PermissionError(reason)
            
            return func(path, *args, **kwargs)
        
        return wrapper
    return decorator

if __name__ == "__main__":
    # Test self-protection
    logging.basicConfig(level=logging.INFO)
    
    protection = SelfProtection()
    
    print("\n✅ Self-Protection System Active")
    print(f"Protected files: {len(protection.protected_files)}")
    
    # Test some operations
    test_paths = [
        "backend/agent.py",
        "backend/self_protection.py",
        "backend/config.yaml",
        "/tmp/test.txt"
    ]
    
    operations = ["read", "write", "delete"]
    
    print("\nTesting operations:")
    for path in test_paths:
        print(f"\nPath: {path}")
        for op in operations:
            allowed, reason = protection.validate_operation(op, path)
            status = "✅" if allowed else "❌"
            print(f"  {status} {op}: {reason}")
