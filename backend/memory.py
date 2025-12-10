"""Agent Memory System - Long-term Learning

ChromeDB Vector Database + Conversation History
Agent learns from past experiences and improves
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import deque


class ConversationMemory:
    """Recent conversation history (last 100 messages)"""
    def __init__(self, max_history: int = 100):
        self.history = deque(maxlen=max_history)
    
    def add(self, role: str, content: str):
        """Add message to history"""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_context(self, last_n: int = 10) -> List[Dict]:
        """Get last N messages for LLM context"""
        return list(self.history)[-last_n:]
    
    def clear(self):
        """Clear history"""
        self.history.clear()


class ActionMemory:
    """Remember what actions worked/failed"""
    def __init__(self):
        self.actions = []
    
    def record_action(self, action: str, parameters: Dict, result: Dict, success: bool):
        """Log action and result"""
        self.actions.append({
            "action": action,
            "parameters": parameters,
            "result": result,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
    
    def find_similar_actions(self, action: str, limit: int = 5) -> List[Dict]:
        """Find similar past actions"""
        similar = [a for a in self.actions if a["action"] == action]
        return similar[-limit:]
    
    def get_success_rate(self, action: str) -> float:
        """Calculate success rate for action type"""
        actions = [a for a in self.actions if a["action"] == action]
        if not actions:
            return 0.0
        successful = sum(1 for a in actions if a["success"])
        return successful / len(actions)


class GameMemory:
    """Remember game states and strategies"""
    def __init__(self):
        self.game_sessions = []
        self.strategies = {}
    
    def start_session(self, game: str):
        """Start new game session"""
        self.game_sessions.append({
            "game": game,
            "start_time": datetime.now().isoformat(),
            "actions": [],
            "score": 0
        })
    
    def record_game_action(self, action: str, result: Dict):
        """Record action in current game session"""
        if self.game_sessions:
            self.game_sessions[-1]["actions"].append({
                "action": action,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
    
    def save_strategy(self, game: str, strategy: str, effectiveness: float):
        """Save winning strategy"""
        if game not in self.strategies:
            self.strategies[game] = []
        self.strategies[game].append({
            "strategy": strategy,
            "effectiveness": effectiveness,
            "saved_at": datetime.now().isoformat()
        })
    
    def get_best_strategy(self, game: str) -> Optional[Dict]:
        """Get best strategy for game"""
        if game not in self.strategies:
            return None
        return max(self.strategies[game], key=lambda x: x["effectiveness"])


class AgentMemory:
    """Main memory manager"""
    def __init__(self):
        self.conversation = ConversationMemory()
        self.actions = ActionMemory()
        self.games = GameMemory()
    
    def export(self) -> Dict:
        """Export all memory"""
        return {
            "conversation": list(self.conversation.history),
            "actions": self.actions.actions,
            "game_sessions": self.games.game_sessions,
            "strategies": self.games.strategies
        }
    
    def import_memory(self, data: Dict):
        """Import memory from file"""
        for msg in data.get("conversation", []):
            self.conversation.history.append(msg)
        self.actions.actions = data.get("actions", [])
        self.games.game_sessions = data.get("game_sessions", [])
        self.games.strategies = data.get("strategies", {})
