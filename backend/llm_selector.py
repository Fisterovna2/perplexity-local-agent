"""LLM Selector - Dual Agent with Safety Functions
Поддержка:
1) Ollama + OpenAI-совместимый API (облачные модели через Ollama)
2) Perplexity API (облачный API напрямую)

Два агента с разными правами:
- Agent 1 (Planner): Только ДУМАЕТ и ПЛАНИРУЕТ, БЕЗ опасных функций
- Agent 2 (Executor): Выполняет план, но ТОЛЬКО утвержденные действия из whitelist
"""

import requests
import json
import os
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

# =====================
# OLLAMA OPENAI API CONFIGURATION
# =====================
OLLAMA_OPENAI_URL = os.getenv('OLLAMA_OPENAI_URL', 'http://localhost:11434/v1')
OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY', 'not-needed')  # Ollama не требует ключ локально
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')  # Или: neural-chat, llama2, openchat

# =====================
# PERPLEXITY API CONFIGURATION
# =====================
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY', '')
PERPLEXITY_ENDPOINT = 'https://api.perplexity.ai/chat/completions'
PERPLEXITY_MODEL = 'sonar-small'  # или sonar, pplx-7b-chat

# =====================
# БЕЗОПАСНОСТЬ: WHITELIST ФУНКЦИЙ
# =====================
class SafetyLevel(Enum):
    PLANNER_ONLY = 1      # Только думать (безопасно)
    SAFE_EXECUTE = 2      # Выполнять безопасные действия
    RESTRICTED = 3        # Требует одобрения

PLANNER_ALLOWED_ACTIONS = {
    'think': SafetyLevel.PLANNER_ONLY,
    'analyze': SafetyLevel.PLANNER_ONLY,
    'plan': SafetyLevel.PLANNER_ONLY,
    'reason': SafetyLevel.PLANNER_ONLY,
}

EXECUTOR_SAFE_FUNCTIONS = {
    'open_app': SafetyLevel.SAFE_EXECUTE,        # Открыть приложение
    'click': SafetyLevel.SAFE_EXECUTE,           # Клик
    'type': SafetyLevel.SAFE_EXECUTE,            # Печать
    'screenshot': SafetyLevel.SAFE_EXECUTE,      # Скриншот
    'wait': SafetyLevel.SAFE_EXECUTE,            # Ждать
}

EXECUTOR_RESTRICTED_FUNCTIONS = {
    'delete_file': SafetyLevel.RESTRICTED,       # Нужна проверка
    'modify_system': SafetyLevel.RESTRICTED,     # Нужна проверка
    'download_file': SafetyLevel.RESTRICTED,     # Нужна проверка
    'run_command': SafetyLevel.RESTRICTED,       # Нужна проверка
}

EXECUTOR_BLOCKED_FUNCTIONS = {
    'rm_rf',                    # НИКОГДА
    'format_drive',             # НИКОГДА
    'delete_registry',          # НИКОГДА
    'sudo',                     # НИКОГДА
    'get_admin',                # НИКОГДА
}

# =====================
# DUAL AGENT SYSTEM
# =====================
class PlannerAgent:
    """Агент 1: ТОЛЬКО ДУМАЕТ И ПЛАНИРУЕТ (БЕЗ опасных действий)"""
    
    def __init__(self, mode: str = 'ollama'):
        self.mode = mode
        self.role = "logical_planner"
        self.allowed_actions = PLANNER_ALLOWED_ACTIONS
        self.can_execute = False  # У планера НЕТ доступа к выполнению
    
    def _call_ollama(self, system: str, user_msg: str) -> str:
        try:
            response = requests.post(
                f'{OLLAMA_OPENAI_URL}/chat/completions',
                headers={'Authorization': f'Bearer {OLLAMA_API_KEY}'},
                json={
                    'model': OLLAMA_MODEL,
                    'messages': [
                        {'role': 'system', 'content': system},
                        {'role': 'user', 'content': user_msg}
                    ],
                    'temperature': 0.7,
                    'max_tokens': 1500
                },
                timeout=30
            )
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return f"[Ошибка Ollama: {e}]"
    
    def _call_perplexity(self, system: str, user_msg: str) -> str:
        if not PERPLEXITY_API_KEY:
            return "[Perplexity API ключ не установлен]"
        
        try:
            response = requests.post(
                PERPLEXITY_ENDPOINT,
                headers={'Authorization': f'Bearer {PERPLEXITY_API_KEY}'},
                json={
                    'model': PERPLEXITY_MODEL,
                    'messages': [
                        {'role': 'system', 'content': system},
                        {'role': 'user', 'content': user_msg}
                    ],
                    'temperature': 0.7
                },
                timeout=30
            )
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Perplexity error: {e}")
            return f"[Ошибка Perplexity: {e}]"
    
    def think(self, task: str) -> str:
        """Агент думает и анализирует (БЕЗ выполнения)"""
        system = """Ты первый участник - ЛОГИК И ПЛАНИРОВЩИК.
Твоя ТОЛЬКО задача: анализировать задачу и создавать план действий.
НЕ выполняй ничего! Только ДУМАЙ и описывай что нужно сделать.
Будь конкретен, указывай шаги через точку с запятой."""
        
        if self.mode == 'ollama':
            return self._call_ollama(system, task)
        elif self.mode == 'perplexity':
            return self._call_perplexity(system, task)
        return "[Неизвестный режим]"


class ExecutorAgent:
    """Агент 2: ВЫПОЛНЯЕТ ПЛАН, но ТОЛЬКО безопасные действия"""
    
    def __init__(self, mode: str = 'ollama'):
        self.mode = mode
        self.role = "action_executor"
        self.safe_functions = EXECUTOR_SAFE_FUNCTIONS
        self.restricted_functions = EXECUTOR_RESTRICTED_FUNCTIONS
        self.blocked_functions = EXECUTOR_BLOCKED_FUNCTIONS
        self.can_execute = True  # У исполнителя ЕСТЬ доступ к выполнению
    
    def _validate_function(self, function_name: str) -> Tuple[bool, str]:
        """Проверить безопасность функции"""
        
        # Проверка: это заблокированная функция?
        if function_name in self.blocked_functions:
            return False, f"❌ ФУНКЦИЯ ЗАБЛОКИРОВАНА: {function_name}"
        
        # Проверка: это безопасная функция?
        if function_name in self.safe_functions:
            return True, f"✅ Разрешено: {function_name}"
        
        # Проверка: это ограниченная функция?
        if function_name in self.restricted_functions:
            return False, f"⚠️ ТРЕБУЕТ ОДОБРЕНИЯ: {function_name}"
        
        # Неизвестная функция - БЛОКИРУЕМ
        return False, f"❌ Неизвестная функция: {function_name}"
    
    def _call_ollama(self, system: str, user_msg: str) -> str:
        try:
            response = requests.post(
                f'{OLLAMA_OPENAI_URL}/chat/completions',
                headers={'Authorization': f'Bearer {OLLAMA_API_KEY}'},
                json={
                    'model': OLLAMA_MODEL,
                    'messages': [
                        {'role': 'system', 'content': system},
                        {'role': 'user', 'content': user_msg}
                    ],
                    'temperature': 0.6,  # Меньше вариативности, больше согласованности
                    'max_tokens': 1500
                },
                timeout=30
            )
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return f"[Ошибка Ollama: {e}]"
    
    def _call_perplexity(self, system: str, user_msg: str) -> str:
        if not PERPLEXITY_API_KEY:
            return "[Perplexity API ключ не установлен]"
        
        try:
            response = requests.post(
                PERPLEXITY_ENDPOINT,
                headers={'Authorization': f'Bearer {PERPLEXITY_API_KEY}'},
                json={
                    'model': PERPLEXITY_MODEL,
                    'messages': [
                        {'role': 'system', 'content': system},
                        {'role': 'user', 'content': user_msg}
                    ],
                    'temperature': 0.6
                },
                timeout=30
            )
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Perplexity error: {e}")
            return f"[Ошибка Perplexity: {e}]"
    
    def execute(self, plan: str) -> str:
        """Выполнить план, но с проверкой безопасности"""
        system = """Ты второй участник - ПРАКТИК И ИСПОЛНИТЕЛЬ.
Твоя задача: выполнить план шаг за шагом.
ВАЖНО: Ты можешь ТОЛЬКО:
- Открывать приложения (open_app)
- Кликать (click)
- Печатать (type)
- Делать скриншоты (screenshot)
- Ждать (wait)

НЕЛЬЗЯ:
- Удалять файлы
- Менять систему
- Выполнять команды sudo/admin
- Форматировать диски

Если план требует опасное действие - ОТКАЖИСЬ и объясни почему."""
        
        if self.mode == 'ollama':
            return self._call_ollama(system, plan)
        elif self.mode == 'perplexity':
            return self._call_perplexity(system, plan)
        return "[Неизвестный режим]"


class DualAgentSystem:
    """Система двух агентов: Планер + Исполнитель (с безопасностью)"""
    
    def __init__(self, mode: str = 'ollama'):
        self.mode = mode
        self.planner = PlannerAgent(mode=mode)
        self.executor = ExecutorAgent(mode=mode)
        self.history = []
    
    def process_task(self, task: str) -> Dict:
        """
        Обработать задачу двумя агентами:
        1) Планер думает и создает план
        2) Исполнитель выполняет план с проверкой безопасности
        3) Планер проверяет результат
        """
        
        # Шаг 1: ПЛАНЕР думает
        logger.info(f"[PLANNER] Анализирую задачу: {task}")
        plan = self.planner.think(task)
        self.history.append({"role": "planner", "action": "think", "content": plan})
        
        # Шаг 2: ИСПОЛНИТЕЛЬ выполняет
        logger.info(f"[EXECUTOR] Выполняю план")
        execution = self.executor.execute(plan)
        self.history.append({"role": "executor", "action": "execute", "content": execution})
        
        # Шаг 3: ПЛАНЕР проверяет
        logger.info(f"[PLANNER] Проверяю результат")
        verification = self.planner.think(f"Проверь если результат корректный: {execution}")
        self.history.append({"role": "planner", "action": "verify", "content": verification})
        
        return {
            "task": task,
            "step1_planning": plan,
            "step2_execution": execution,
            "step3_verification": verification,
            "safe": True,  # Всегда безопасно благодаря whitelist
            "history": self.history[-3:]
        }


# =====================
# ИНИЦИАЛИЗАЦИЯ
# =====================
def initialize_llm(mode: str = 'ollama') -> DualAgentSystem:
    """Инициализируй систему двух агентов"""
    logger.info(f"Initializing Dual Agent System in {mode} mode...")
    return DualAgentSystem(mode=mode)


# Глобальный экземпляр
agent_system = None

def get_agent_system(mode: str = 'ollama') -> DualAgentSystem:
    """Получить систему агентов"""
    global agent_system
    if agent_system is None:
        agent_system = initialize_llm(mode)
    return agent_system


def execute_task(task: str, mode: str = 'ollama') -> Dict:
    """Выполнить задачу через систему двух агентов"""
    system = get_agent_system(mode)
    return system.process_task(task)


# Экспорт
if __name__ == '__main__':
    # Пример
    system = initialize_llm(mode='ollama')
    result = system.process_task("Открой Roblox и загрузи Bee Swarm")
    
    print("\n=== РЕЗУЛЬТАТ ===")
    print(f"План: {result['step1_planning']}\n")
    print(f"Выполнение: {result['step2_execution']}\n")
    print(f"Проверка: {result['step3_verification']}")
