# Telegram Bot - Управление агентом через телеграм
# Полный контроль агента из бота

from flask import Blueprint, request, jsonify
import logging
from typing import Dict
import json

logger = logging.getLogger(__name__)

class TelegramBotController:
    """Контроллер телеграм бота"""
    
    def __init__(self, token: str, agent):
        self.token = token
        self.agent = agent
        self.allowed_users = []
    
    def add_authorized_user(self, user_id: int):
        """Добавить авторизованного пользователя"""
        self.allowed_users.append(user_id)
        logger.info(f"Добавлен пользователь: {user_id}")
    
    def is_authorized(self, user_id: int) -> bool:
        """Проверить, авторизован ли пользователь"""
        return user_id in self.allowed_users
    
    def handle_command(self, user_id: int, command: str) -> Dict:
        """Обработать команду из телеграма"""
        if not self.is_authorized(user_id):
            return {'error': 'Неавторизованный аккесс'}
        
        if command == '/start':
            return self.cmd_start()
        elif command == '/propose':
            return self.cmd_propose()
        elif command == '/approve':
            return self.cmd_approve()
        elif command == '/reject':
            return self.cmd_reject()
        elif command == '/auto_on':
            return self.cmd_auto_on()
        elif command == '/auto_off':
            return self.cmd_auto_off()
        elif command == '/stats':
            return self.cmd_stats()
        else:
            return {'error': 'Неизвестная команда'}
    
    def cmd_start(self) -> Dict:
        """Команда /start"""
        return {
            'message': '🤖 AI Agent Online!',
            'commands': [
                '/propose - Предложить новый проект',
                '/approve - Одобрить проект',
                '/reject - Отклонить проект',
                '/auto_on - Ключить автомод',
                '/auto_off - Отключить автомод',
                '/stats - Показать статистику'
            ]
        }
    
    def cmd_propose(self) -> Dict:
        """Команда /propose"""
        idea = self.agent.propose_next_project()
        return {
            'idea_id': idea['id'],
            'description': idea['description'],
            'priority': idea['priority']
        }
    
    def cmd_approve(self) -> Dict:
        """Команда /approve"""
        if self.agent.approve_project():
            self.agent.execute_project(self.agent.current_project)
            return {'status': 'Проект одобрен и выполняются'}
        return {'error': 'Нет в ожидании проекта'}
    
    def cmd_reject(self) -> Dict:
        """Команда /reject"""
        if self.agent.reject_project():
            return {'status': 'Проект отклонен'}
        return {'error': 'Нет в ожидании проекта'}
    
    def cmd_auto_on(self) -> Dict:
        """Команда /auto_on"""
        self.agent.start_auto_mode()
        return {'status': 'Автомод включен'}
    
    def cmd_auto_off(self) -> Dict:
        """Команда /auto_off"""
        self.agent.stop_auto_mode()
        return {'status': 'Автомод отключен'}
    
    def cmd_stats(self) -> Dict:
        """Команда /stats"""
        stats = self.agent.get_stats()
        return {
            'approved_projects': stats['approved'],
            'rejected_projects': stats['rejected'],
            'current_project': stats['current_project']['description'] if stats['current_project'] else 'Нет',
            'auto_mode': stats['running']
        }

def create_telegram_blueprint(agent) -> Blueprint:
    """Создать blueprint для телеграм апи"""
    bp = Blueprint('telegram', __name__, url_prefix='/api/v1/telegram')
    bot = TelegramBotController('YOUR_BOT_TOKEN', agent)
    
    @bp.route('/command', methods=['POST'])
    def handle_telegram_command():
        """Обработчик команд телеграма"""
        data = request.json
        user_id = data.get('user_id')
        command = data.get('command')
        
        result = bot.handle_command(user_id, command)
        logger.info(f"Команда: {command} от {user_id}")
        
        return jsonify(result)
    
    @bp.route('/authorize', methods=['POST'])
    def authorize_user():
        """Авторизация пользователя"""
        data = request.json
        user_id = data.get('user_id')
        bot.add_authorized_user(user_id)
        return jsonify({'status': f'Пользователь {user_id} авторизован'})
    
    return bp
