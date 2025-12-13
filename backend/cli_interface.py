#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI Interface for Perplexity Local Agent
Provides command-line interface for controlling the agent with command grouping
"""

import os
import sys
from typing import Dict, List, Optional

class CLIInterface:
    """Interactive CLI interface with command grouping"""
    
    def __init__(self):
        self.command_groups = {
            'games': {
                'description': '🎮 Игры и автоматизация игр',
                'commands': {
                    '/game_roblox': 'Автоматизация Roblox',
                    '/game_dota2': 'Автоматизация Dota 2',
                    '/game_beeswarm': 'Автоматизация Bee Swarm Simulator',
                    '/game_status': 'Статус игровой автоматизации'
                }
            },
            'projects': {
                'description': '📋 Планирование и управление проектами',
                'commands': {
                    '/project_new': 'Создать новый проект',
                    '/project_plan': 'Планирование задач проекта',
                    '/project_status': 'Статус текущих проектов',
                    '/project_decompose': 'Декомпозиция задачи'
                }
            },
            '3d_modeling': {
                'description': '🎨 3D моделирование и Blender',
                'commands': {
                    '/blender_model': 'Создать 3D модель в Blender',
                    '/blender_script': 'Выполнить Blender скрипт',
                    '/blender_render': 'Рендер сцены',
                    '/blender_export': 'Экспорт модели'
                }
            },
            'automation': {
                'description': '⚙️ Автоматизация и управление',
                'commands': {
                    '/input_mouse': 'Управление мышью',
                    '/input_keyboard': 'Управление клавиатурой',
                    '/vision_screen': 'Анализ экрана',
                    '/vision_control': 'Управление через компьютерное зрение'
                }
            },
            'web': {
                'description': '🌐 Веб-автоматизация',
                'commands': {
                    '/web_scan': 'Сканирование сайта (VirusTotal)',
                    '/web_automate': 'Автоматизация браузера',
                    '/web_scrape': 'Извлечение данных с веб-страниц'
                }
            },
            'communication': {
                'description': '💬 Коммуникация',
                'commands': {
                    '/telegram_send': 'Отправить сообщение в Telegram',
                    '/telegram_dialog': 'Диалоговая система Telegram',
                    '/telegram_schedule': 'Запланировать сообщение'
                }
            },
            'system': {
                'description': '🔧 Системные команды',
                'commands': {
                    '/mode_brain': 'Изменить режим мозга (normal/fairplay/curious)',
                    '/mode_safety': 'Изменить режим безопасности',
                    '/model_select': 'Выбрать LLM модель',
                    '/memory_status': 'Статус долговременной памяти',
                    '/status': 'Общий статус системы',
                    '/help': 'Справка по командам'
                }
            }
        }
    
    def show_commands(self) -> str:
        """Display all command groups"""
        output = ["\n=== Доступные группы команд ==="]
        output.append("Используйте /commands <группа> для просмотра команд группы\n")
        
        for group_name, group_data in self.command_groups.items():
            output.append(f"{group_data['description']}")
            output.append(f"  /commands {group_name}\n")
        
        return "\n".join(output)
    
    def show_group_commands(self, group_name: str) -> str:
        """Display commands in a specific group"""
        if group_name not in self.command_groups:
            return f"❌ Группа '{group_name}' не найдена. Используйте /commands для списка групп."
        
        group = self.command_groups[group_name]
        output = [f"\n=== {group['description']} ==="]
        
        for cmd, description in group['commands'].items():
            output.append(f"  {cmd:<25} - {description}")
        
        return "\n".join(output)
    
    def get_all_commands(self) -> List[str]:
        """Get list of all available commands"""
        commands = []
        for group_data in self.command_groups.values():
            commands.extend(group_data['commands'].keys())
        return commands
    
    def parse_command(self, user_input: str) -> Dict[str, any]:
        """Parse user command input"""
        parts = user_input.strip().split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Handle /commands group display
        if command == '/commands':
            if args:
                return {'command': '/commands', 'group': args, 'args': ''}
            return {'command': '/commands', 'group': None, 'args': ''}
        
        return {'command': command, 'args': args}
    
    def run_interactive(self):
        """Run interactive CLI loop"""
        print("\n" + "="*60)
        print("    Perplexity Local Agent - Interactive CLI")
        print("="*60)
        print("Введите /commands для списка всех команд")
        print("Введите /help для справки")
        print("Введите 'exit' или 'quit' для выхода")
        print("="*60 + "\n")
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 До свидания!")
                    break
                
                parsed = self.parse_command(user_input)
                
                # Handle special commands
                if parsed['command'] == '/commands':
                    if parsed.get('group'):
                        print(self.show_group_commands(parsed['group']))
                    else:
                        print(self.show_commands())
                    continue
                
                if parsed['command'] == '/help':
                    print(self.show_commands())
                    print("\nДля получения справки по конкретной команде: <команда> --help")
                    continue
                
                # Check if command exists
                all_commands = self.get_all_commands()
                if parsed['command'] not in all_commands:
                    print(f"❌ Неизвестная команда: {parsed['command']}")
                    print("Используйте /commands для списка доступных команд")
                    continue
                
                # Execute command (will be integrated with actual agent)
                print(f"\n🚀 Выполнение команды: {parsed['command']}")
                if parsed['args']:
                    print(f"   Аргументы: {parsed['args']}")
                
                # TODO: Integrate with actual agent command execution
                print("⚠️  Интеграция с агентом в разработке")
                
            except KeyboardInterrupt:
                print("\n\n👋 Прервано пользователем. До свидания!")
                break
            except Exception as e:
                print(f"\n❌ Ошибка: {str(e)}")

def main():
    """Main entry point for CLI interface"""
    cli = CLIInterface()
    cli.run_interactive()

if __name__ == '__main__':
    main()
