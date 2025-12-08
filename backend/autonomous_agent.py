# Автономный Агент - Рабочий самостоятельный база запросов
# Предусмотрев проекты, предлагает идеи, сам их выполняет

import json
import time
import threading
import random
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class AutonomousAgent:
    """Автономный агент выполняет очередь задач"""
    
    def __init__(self):
        self.tasks = {}
        self.current_task = None
        self.running = False
        self.ideas = [
            "Открыть Roblox и поиграть обед",
            "Составить список сайтов для программирования",
            "Создать Python скрипт для автоматизации",
            "Загрузить часть базы реестров",
            "Исследовать оригинальные числа и проверить расчета"
        ]
        self.completed_projects = []
    
    def generate_ideas(self) -> Dict:
        """Генерирует случайную идею"""
        idea_text = random.choice(self.ideas)
        return {
            'id': len(self.completed_projects) + 1,
            'description': idea_text,
            'timestamp': datetime.now().isoformat(),
            'status': 'proposed'
        }
    
    def propose_idea(self) -> Dict:
        """Предлагает агентом идея"""
        idea = self.generate_ideas()
        logger.info(f"Предложена идея: {idea}")
        print(f"💡 Идея #{idea['id']}: {idea['description']}")
        return idea
    
    def add_task(self, task_id: int, task_data: Dict) -> bool:
        """Добавить задачу в очередь"""
        self.tasks[task_id] = task_data
        logger.info(f"Задача {task_id} добавлена: {task_data}")
        return True
    
    def get_next_task(self):
        """Получить следующую задачу со статусом pending"""
        for task_id, task in self.tasks.items():
            if task.get("status") == "pending":
                return task_id, task
        return None, None
    
    def execute_task(self, task):
        """Выполнить задачу"""
        logger.info(f"Выполняю задачу: {task}")
        print(f"▶️ Выполняю: {task}")
        
        task_type = task.get("type")
        
        if task_type == "game":
            self.execute_game(task)
        elif task_type == "task":
            self.execute_generic_task(task)
        elif task_type == "project":
            self.execute_project(task)
    
    def execute_game(self, task):
        """Выполнить игровую задачу"""
        game = task.get("game")
        game_task = task.get("task")
        
        print(f"🎮 Запускаю {game}: {game_task}")
        logger.info(f"Game task: {game} - {game_task}")
        
        # Имитация работы
        time.sleep(2)
    
    def execute_generic_task(self, task):
        """Выполнить обычную задачу"""
        text = task.get("text")
        
        print(f"📝 Выполняю: {text}")
        logger.info(f"Task: {text}")
        
        time.sleep(2)
    
    def execute_project(self, task):
        """Выполнить проект"""
        project_name = task.get("project")
        description = task.get("description")
        
        print(f"🚀 Проект: {project_name}")
        print(f"📋 Описание: {description}")
        logger.info(f"Project: {project_name} - {description}")
        
        time.sleep(2)
    
    def run(self):
        """Основной цикл агента"""
        self.running = True
        print("🤖 Автономный агент запущен!")
        
        while self.running:
            task_id, task = self.get_next_task()
            
            if task:
                print(f"\n✅ Найдена задача ID {task_id}")
                self.current_task = task_id
                
                task["status"] = "running"
                
                try:
                    self.execute_task(task)
                    task["status"] = "done"
                    self.completed_projects.append(task_id)
                except Exception as e:
                    task["status"] = "error"
                    logger.error(f"Error: {str(e)}")
                
                print(f"✅ Задача {task_id} завершена\n")
            else:
                # Если нет задач, генерируй идеи
                print("💡 Нет задач в очереди. Генерирую идеи...")
                self.propose_idea()
            
            time.sleep(2)
    
    def stop(self):
        """Остановить агента"""
        self.running = False
        print("❌ Агент остановлен")

if __name__ == "__main__":
    agent = AutonomousAgent()
    agent.run()
