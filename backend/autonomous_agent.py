# Autonomous Agent - Работает самостоятельно без запросов
# Придумывает проекты, предлагает идеи, сам их выполняет

import json
import time
import threading
import random
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ProjectGenerator:
    """Генератор идей для проектов"""
    
    def __init__(self):
        self.ideas = [
            "Открыть Roblox и пройти обби",
            "Составить список сайтов для программистов",
            "Создать Python скрипт для автоматизации",
            "Загрузить часть банка регистров",
            "Придумать оригинальные числа и проверить способ расчёта"
        ]
        self.completed_projects = []
    
    def generate_idea(self) -> Dict:
        """Генерирует случайную идею"""
        idea_text = random.choice(self.ideas)
        return {
            'id': len(self.completed_projects) + 1,
            'description': idea_text,
            'timestamp': datetime.now().isoformat(),
            'status': 'proposed',
            'priority': random.randint(1, 5)
        }
    
    def propose_idea(self) -> Dict:
        """Предлагает агентом идею"""
        idea = self.generate_idea()
        logger.info(f"Предложена идея: {idea['description']}")
        return idea

class AutonomousAgent:
    """Автономный агент - работает самостоятельно"""
    
    def __init__(self, vision_controller, input_controller):
        self.generator = ProjectGenerator()
        self.vision = vision_controller
        self.input = input_controller
        self.current_project = None
        self.running = False
        self.approved_ideas = []
        self.rejected_ideas = []
    
    def propose_next_project(self) -> Dict:
        """Предлагает следующий проект"""
        idea = self.generator.propose_idea()
        self.current_project = idea
        return idea
    
    def approve_project(self) -> bool:
        """Одобряет текущий проект"""
        if self.current_project:
            self.current_project['status'] = 'approved'
            self.approved_ideas.append(self.current_project)
            logger.info(f"Проект одобрен: {self.current_project['description']}")
            return True
        return False
    
    def reject_project(self) -> bool:
        """Отклоняет проект"""
        if self.current_project:
            self.current_project['status'] = 'rejected'
            self.rejected_ideas.append(self.current_project)
            logger.info(f"Проект отклонён: {self.current_project['description']}")
            return True
        return False
    
    def execute_project(self, project: Dict) -> bool:
        """Выполняет проект"""
        logger.info(f"Выполняю проект: {project['description']}")
        project['status'] = 'running'
        time.sleep(2)
        project['status'] = 'completed'
        logger.info(f"Проект завершён")
        return True
    
    def start_auto_mode(self):
        """Запускает автономный режим"""
        self.running = True
        logger.info("Автономный режим включен")
        
        def auto_loop():
            while self.running:
                self.propose_next_project()
                time.sleep(2)  # Можно одобрить через API/Telegram
        
        thread = threading.Thread(target=auto_loop, daemon=True)
        thread.start()
    
    def stop_auto_mode(self):
        """Отключает автономный режим"""
        self.running = False
        logger.info("Автономный режим отключен")
    
    def get_stats(self) -> Dict:
        """Гет статистику"""
        return {
            'approved': len(self.approved_ideas),
            'rejected': len(self.rejected_ideas),
            'current_project': self.current_project,
            'running': self.running
        }
