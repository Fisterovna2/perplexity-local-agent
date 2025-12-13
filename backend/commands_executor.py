#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command Executor - Handles all CLI command execution with real module integration
Этот файл содержит ВСЕ команды агента с реальной интеграцией модулей
"""

import os
import sys
from typing import Dict, Any, Optional

# Import all agent modules
try:
    from game_automation import GameAutomation
    from blender_34 import Blender3DModule
    from input_control import InputControl
    from tools_advanced import AdvancedTools
    from telegram_bot import TelegramBot
    from planner import TaskPlanner
    from memory import AgentMemory
    from main_entry import load_config, save_config
except ImportError as e:
    print(f"⚠️ Import error: {e}")

class CommandExecutor:
    """Executes all CLI commands with module integration"""
    
    def __init__(self):
        # Initialize all modules
        self.game_automation = GameAutomation()
        self.blender = Blender3DModule()
        self.input_control = InputControl()
        self.tools = AdvancedTools()
        self.telegram = TelegramBot()
        self.planner = TaskPlanner()
        self.memory = AgentMemory()
        
        # Command mapping - connects command strings to methods
        self.commands = self._build_command_map()
    
    def _build_command_map(self) -> Dict[str, callable]:
        """Build comprehensive command mapping"""
        return {
            # 🎮 ИГРЫ - Game Automation Commands
            '/game_roblox_play': lambda args: self.game_automation.roblox_play(args.get('game_id', ''), args.get('task', 'play')),
            '/game_roblox_farm': lambda args: self.game_automation.roblox_play('', 'farm'),
            '/game_roblox_stop': lambda args: self.game_automation.stop(),
            '/game_dota2_play': lambda args: self.game_automation.dota2_play(args.get('mode', 'turbo')),
            '/game_dota2_ranked': lambda args: self.game_automation.dota2_play('ranked'),
            '/game_dota2_turbo': lambda args: self.game_automation.dota2_play('turbo'),
            '/game_beeswarm_farm': lambda args: self.game_automation.bee_swarm_farm(int(args.get('duration', 3600))),
            '/game_status': lambda args: self.game_automation.get_status(),
            '/game_stop_all': lambda args: self.game_automation.stop(),
            
            # 📋 ПРОЕКТЫ - Project Management
            '/project_new': lambda args: self.planner.create_project(args.get('name', 'New Project')),
            '/project_plan': lambda args: self.planner.plan_tasks(args.get('project_id')),
            '/project_status': lambda args: self.planner.get_status(),
            '/project_decompose': lambda args: self.planner.decompose_task(args.get('task')),
            '/project_list': lambda args: self.planner.list_projects(),
            '/project_delete': lambda args: self.planner.delete_project(args.get('project_id')),
            
            # 🎨 3D МОДЕЛИРОВАНИЕ - Blender 3D
            '/blender_model': lambda args: self.blender.create_model(args.get('prompt')),
            '/blender_script': lambda args: self.blender.execute_script(args.get('script')),
            '/blender_render': lambda args: self.blender.render_scene(),
            '/blender_export': lambda args: self.blender.export_model(args.get('format', 'obj')),
            '/blender_open': lambda args: self.blender.open_blender(),
            '/blender_cube': lambda args: self.blender.create_model('cube'),
            '/blender_sphere': lambda args: self.blender.create_model('sphere'),
            
            # ⚙️ АВТОМАТИЗАЦИЯ - Input Control
            '/mouse_click': lambda args: self.input_control.mouse_click(int(args.get('x', 960)), int(args.get('y', 540))),
            '/mouse_move': lambda args: self.input_control.mouse_move(int(args.get('x')), int(args.get('y'))),
            '/mouse_drag': lambda args: self.input_control.mouse_drag(int(args.get('x1')), int(args.get('y1')), int(args.get('x2')), int(args.get('y2'))),
            '/keyboard_type': lambda args: self.input_control.type_text(args.get('text')),
            '/keyboard_press': lambda args: self.input_control.press_key(args.get('key')),
            '/keyboard_hotkey': lambda args: self.input_control.hotkey(args.get('keys').split('+')),
            '/screen_capture': lambda args: self.input_control.screenshot(args.get('path', 'screenshot.png')),
            '/screen_region': lambda args: self.input_control.screenshot_region(int(args.get('x')), int(args.get('y')), int(args.get('w')), int(args.get('h'))),
            
            # 🌐 ВЕБ - Web Automation
            '/web_scan': lambda args: self.tools.scan_url(args.get('url')),
            '/web_open': lambda args: self.tools.open_browser(args.get('url')),
            '/web_search': lambda args: self.tools.web_search(args.get('query')),
            '/web_download': lambda args: self.tools.download_file(args.get('url'), args.get('path')),
            
            # 💬 TELEGRAM - Communication
            '/tg_send': lambda args: self.telegram.send_message(args.get('chat_id'), args.get('text')),
            '/tg_photo': lambda args: self.telegram.send_photo(args.get('chat_id'), args.get('photo')),
            '/tg_status': lambda args: self.telegram.get_status(),
            
            # 🔧 СИСТЕМА - System Commands
            '/mode_brain': lambda args: self._set_brain_mode(args.get('mode')),
            '/mode_safety': lambda args: self._set_safety_mode(args.get('mode')),
            '/memory_save': lambda args: self.memory.save(args.get('key'), args.get('value')),
            '/memory_get': lambda args: self.memory.get(args.get('key')),
            '/memory_status': lambda args: self.memory.get_status(),
            '/config_get': lambda args: self._get_config(args.get('key')),
            '/config_set': lambda args: self._set_config(args.get('key'), args.get('value')),
        }
    
    def execute(self, command: str, args: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a command with arguments"""
        if args is None:
            args = {}
        
        if command not in self.commands:
            return {'success': False, 'error': f'Unknown command: {command}'}
        
        try:
            result = self.commands[command](args)
            return {'success': True, 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _set_brain_mode(self, mode: str) -> Dict[str, Any]:
        """Set brain mode (ollama/api/comet_chat)"""
        config = load_config()
        config['llm']['brain_mode'] = mode
        save_config(config)
        return {'mode': mode, 'message': f'Brain mode set to {mode}'}
    
    def _set_safety_mode(self, mode: str) -> Dict[str, Any]:
        """Set safety mode (normal/fairplay/curious)"""
        config = load_config()
        config['modes']['active'] = mode
        save_config(config)
        return {'mode': mode, 'message': f'Safety mode set to {mode}'}
    
    def _get_config(self, key: str) -> Any:
        """Get config value"""
        config = load_config()
        return config.get(key)
    
    def _set_config(self, key: str, value: Any) -> Dict[str, Any]:
        """Set config value"""
        config = load_config()
        config[key] = value
        save_config(config)
        return {'key': key, 'value': value}

# Create global executor instance
executor = CommandExecutor()
