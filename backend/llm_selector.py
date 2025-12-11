"""LLM Selector - Dual Mode (Ollama Local + API Cloud)
Два режима: локальный Ollama + облачные API
Режим "Два человека" - естественное поведение с вариативностью
"""
import requests
import json
import os
import random
import time
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# =====================
# OLLAMA CONFIGURATION
# =====================
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2')  # или mistral, neural-chat

# =====================
# API CONFIGURATION (Groq - бесплатно!)
# =====================
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GROQ_ENDPOINT = 'https://api.groq.com/openai/v1/chat/completions'
GROQ_MODEL = 'mixtral-8x7b-32768'  # Быстрый и бесплатный

# =====================
# РЕЖИМ "ДВА ЧЕЛОВЕКА"
# =====================
class DualModeAgent:
    """Агент работает как два человека в компьютере"""
    
    def __init__(self, mode: str = 'ollama'):
        """
        mode: 'ollama' (локально) или 'groq' (облачно, бесплатно)
        """
        self.mode = mode
        self.personality_1 = "logical_planner"  # Планирует
        self.personality_2 = "action_executor"  # Выполняет
        self.conversation_history = []
        self.natural_delays = True  # Естественные паузы
        self.random_typos = False  # Иногда опечатки
        self.thinks_out_loud = True  # Думает вслух
        
    def _get_natural_delay(self) -> float:
        """Имитирует человеческую скорость чтения/печати"""
        if self.natural_delays:
            return random.uniform(0.5, 2.0)
        return 0
    
    def _ollama_chat(self, system_prompt: str, user_message: str) -> str:
        """Локальный Ollama - полностью бесплатно, оффлайн"""
        try:
            time.sleep(self._get_natural_delay())
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            self.conversation_history.append({"role": "user", "content": user_message})
            
            response = requests.post(
                f'{OLLAMA_BASE_URL}/api/chat',
                json={
                    'model': OLLAMA_MODEL,
                    'messages': messages,
                    'stream': False,
                    'temperature': 0.7  # Вариативность ответов
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()['message']['content']
                self.conversation_history.append({"role": "assistant", "content": result})
                return result
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return "[Ошибка подключения к Ollama]"
                
        except Exception as e:
            logger.error(f"Ollama exception: {e}")
            return f"[Ошибка: {str(e)}]"
    
    def _groq_chat(self, system_prompt: str, user_message: str) -> str:
        """Облачный Groq API - быстро и бесплатно (нужен API ключ)"""
        if not GROQ_API_KEY:
            return "[Groq API ключ не установлен. Используй Ollama]"
        
        try:
            time.sleep(self._get_natural_delay())
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            self.conversation_history.append({"role": "user", "content": user_message})
            
            response = requests.post(
                GROQ_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2048
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()['choices'][0]['message']['content']
                self.conversation_history.append({"role": "assistant", "content": result})
                return result
            else:
                logger.error(f"Groq error: {response.status_code}")
                return "[Ошибка API Groq]"
                
        except Exception as e:
            logger.error(f"Groq exception: {e}")
            return f"[Ошибка: {str(e)}]"
    
    def think_and_plan(self, task: str) -> str:
        """Личность 1: Логик - планирует действия"""
        system = """Ты первый участник дуэта. Ты логик и планировщик.
Твоя задача: анализировать задачу и создавать четкий план действий.
Отвечай кратко и лаконично (2-3 предложения).
Потом скажи конкретные шаги через точку с запятой."""
        
        return self._execute(system, task)
    
    def execute_action(self, plan: str) -> str:
        """Личность 2: Исполнитель - выполняет план"""
        system = """Ты второй участник дуэта. Ты практик и исполнитель.
Твоя задача: выполнять план и описывать свои действия естественно.
Опиши что ты делаешь, как это выглядит. Будь конкретен и деталей.
"""
        
        return self._execute(system, plan)
    
    def _execute(self, system: str, user_message: str) -> str:
        """Выполняет запрос в зависимости от режима"""
        if self.mode == 'ollama':
            return self._ollama_chat(system, user_message)
        elif self.mode == 'groq':
            return self._groq_chat(system, user_message)
        else:
            return "[Неизвестный режим]"
    
    def dual_mode_response(self, task: str) -> Dict:
        """Получить ответ от обоих агентов (как два человека разговаривают)"""
        # Шаг 1: Логик планирует
        plan = self.think_and_plan(task)
        
        # Шаг 2: Исполнитель выполняет
        execution = self.execute_action(plan)
        
        # Шаг 3: Логик проверяет
        verification = self.think_and_plan(f"Проверь результат: {execution}. Это правильно?")
        
        return {
            "task": task,
            "step1_plan": plan,
            "step2_execution": execution,
            "step3_verification": verification,
            "history": self.conversation_history[-6:]  # Последние 6 сообщений
        }

# =====================
# ИНИЦИАЛИЗАЦИЯ
# =====================
def initialize_llm(mode: str = 'ollama') -> DualModeAgent:
    """Инициализируй агента"""
    logger.info(f"Initializing LLM in {mode} mode...")
    agent = DualModeAgent(mode=mode)
    return agent

# Глобальный экземпляр
llm_selector = None

def init_selector(mode: str = 'ollama'):
    """Инициализируй селектор"""
    global llm_selector
    llm_selector = initialize_llm(mode)
    return llm_selector

def get_response(task: str, mode: str = 'ollama') -> Dict:
    """Получи ответ от агента"""
    global llm_selector
    if llm_selector is None:
        llm_selector = initialize_llm(mode)
    
    return llm_selector.dual_mode_response(task)

# Export
if __name__ == '__main__':
    # Пример использования
    agent = initialize_llm(mode='ollama')  # Используй 'ollama' если он установлен
    
    result = agent.dual_mode_response("Помоги мне открыть Roblox и запустить Bee Swarm")
    
    print("\n=== РЕЗУЛЬТАТ ===")
    print(f"Плана: {result['step1_plan']}")
    print(f"\nВыполнение: {result['step2_execution']}")
    print(f"\nПроверка: {result['step3_verification']}")
