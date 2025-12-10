"""LLM Model Selector - Central Hub for All AI Models

Supports: Sonar, GPT-5.1, Claude Opus 4.5, Gemini 2 Pro, Grok 4.1, Kimi K2,  Claude Sonnet 4.5
User selects model in Comet, agent uses it for ALL decisions
Fair Play Mode ENABLED:
- NO cheats
- NO memory hacking
- NO process injection
- Only screen vision + honest input control (clicks, keys)
- Agent sees what player sees
- Agent plays like a human player
"""

import requests
import json
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import os
from dotenv import load_dotenv

load_dotenv()


class ModelProvider(Enum):
    """Available LLM providers"""
    SONAR = "sonar"
    GPT5_1 = "gpt-5.1"
    CLAUDE_OPUS = "claude-opus-4.5"
    GEMINI_2_PRO = "gemini-2-pro"
    GROK_4_1 = "grok-4.1"
    KIMI_K2 = "kimi-k2"
    CLAUDE_SONNET_45 = "claude-sonnet-4.5"

@dataclass
class ModelConfig:
    """Model configuration"""
    name: str
    provider: ModelProvider
    api_key: Optional[str]
    endpoint: Optional[str]
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 60


class OpenAIConnector:
    """GPT-4o Connector"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "gpt-4o"
        self.base_url = "https://api.openai.com/v1"
    
    def plan_actions(self, user_request: str, available_tools: List[str]) -> Dict[str, Any]:
        """LLM plans multi-step actions"""
        prompt = f"""User request: {user_request}
        
Available tools:
{json.dumps(available_tools, indent=2)}

Generate a detailed step-by-step plan as JSON:
{{
  "steps": [
    {{
      "step_num": 1,
      "action": "tool_name",
      "parameters": {{}},
      "reasoning": "why this action",
      "dependencies": []
    }}
  ],
  "total_steps": number,
  "success_criteria": "how to verify completion"
}}"""
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            result = response.json()["choices"][0]["message"]["content"]
            return json.loads(result)
        except Exception as e:
            return {"error": str(e)}
    
    def reflect(self, action_result: str, original_goal: str) -> str:
        """Self-reflection: Did action work? Need correction?"""
        prompt = f"""Original goal: {original_goal}
Action result: {action_result}

Analyze:
1. Was the goal achieved?
2. What went wrong (if anything)?
3. Next step?

Respond in JSON."""
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return str(e)


class AnthropicConnector:
    """Claude 3.5 Sonnet Connector"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "claude-3-5-sonnet-20241022"
        self.base_url = "https://api.anthropic.com/v1"
    
    def plan_actions(self, user_request: str, available_tools: List[str]) -> Dict[str, Any]:
        """Claude plans actions"""
        prompt = f"""User: {user_request}

Tools available: {json.dumps(available_tools)}

Create detailed JSON plan with steps."""
        
        headers = {"x-api-key": self.api_key, "anthropic-version": "2023-06-01"}
        data = {
            "model": self.model,
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=data,
                timeout=60
            )
            result = response.json()["content"][0]["text"]
            return json.loads(result)
        except Exception as e:
            return {"error": str(e)}


class GoogleConnector:
    """Gemini Pro Connector"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "gemini-pro"
    
    def plan_actions(self, user_request: str, available_tools: List[str]) -> Dict[str, Any]:
        """Gemini plans actions"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        
        prompt = f"""Plan for: {user_request}\nTools: {json.dumps(available_tools)}"""
        
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        try:
            response = requests.post(
                url,
                params={"key": self.api_key},
                json=data,
                timeout=60
            )
            result = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(result)
        except Exception as e:
            return {"error": str(e)}


class OllamaConnector:
    """Local Llama 3 Connector (Ollama)"""
    def __init__(self, endpoint: str = "http://localhost:11434"):
        self.endpoint = endpoint
        self.model = "llama3"
    
    def plan_actions(self, user_request: str, available_tools: List[str]) -> Dict[str, Any]:
        """Local LLM plans actions"""
        prompt = f"""Plan: {user_request}\nTools: {json.dumps(available_tools)}"""
        
        try:
            response = requests.post(
                f"{self.endpoint}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=120
            )
            result = response.json()["response"]
            return json.loads(result)
        except Exception as e:
            return {"error": str(e)}


class PerplexityConnector:
    """Perplexity Pro Connector"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "pplx-7b-chat"
    
    def plan_actions(self, user_request: str, available_tools: List[str]) -> Dict[str, Any]:
        """Perplexity plans with search capability"""
        url = "https://api.perplexity.ai/chat/completions"
        
        prompt = f"Plan: {user_request}\nTools: {json.dumps(available_tools)}"
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            result = response.json()["choices"][0]["message"]["content"]
            return json.loads(result)
        except Exception as e:
            return {"error": str(e)}


class LLMSelector:
    """Central Model Selector - User chooses in Comet"""
    
    def __init__(self):
        self.connectors = {
            ModelProvider.OPENAI: OpenAIConnector(os.getenv("OPENAI_API_KEY", "")),
            ModelProvider.ANTHROPIC: AnthropicConnector(os.getenv("ANTHROPIC_API_KEY", "")),
            ModelProvider.GOOGLE: GoogleConnector(os.getenv("GOOGLE_API_KEY", "")),
            ModelProvider.OLLAMA: OllamaConnector(),
            ModelProvider.PERPLEXITY: PerplexityConnector(os.getenv("PERPLEXITY_API_KEY", "")),
        }
        self.current_model: Optional[ModelProvider] = None
        self.model_history: List[str] = []
    
    def select_model(self, model: ModelProvider) -> str:
        """User selects model in Comet"""
        if model not in self.connectors:
            return f"Model {model} not available"
        
        self.current_model = model
        self.model_history.append(model.value)
        return f"Selected model: {model.value}"
    
    def get_available_models(self) -> List[str]:
        """Get list of available models for Comet dropdown"""
        return [m.value for m in ModelProvider]
    
    def plan_actions(self, user_request: str, available_tools: List[str]) -> Dict[str, Any]:
        """Use selected model to plan actions"""
        if not self.current_model:
            return {"error": "No model selected. Select via Comet first."}
        
        connector = self.connectors.get(self.current_model)
        if not connector:
            return {"error": f"Connector not found for {self.current_model}"}
        
        return connector.plan_actions(user_request, available_tools)
    
    def reflect_on_action(self, action_result: str, original_goal: str) -> str:
        """Self-reflection on action results"""
        if not self.current_model:
            return "No model selected"
        
        connector = self.connectors.get(self.current_model)
        if hasattr(connector, 'reflect'):
            return connector.reflect(action_result, original_goal)
        return "Reflection not available for this model"
    
    def get_current_model(self) -> Optional[str]:
        """Get currently selected model"""
        return self.current_model.value if self.current_model else None


# Test
if __name__ == "__main__":
    selector = LLMSelector()
    print("Available models:", selector.get_available_models())
    selector.select_model(ModelProvider.OPENAI)
    print("Selected:", selector.get_current_model())
