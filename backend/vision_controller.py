# Vision & Input Controller - AI управляет компьютером
# Анализирует экран, видит объекты и управляет мышью/клавиатурой

import pyautogui
import cv2
import numpy as np
import time
import threading
from PIL import ImageGrab
from typing import Tuple, List, Dict
import logging

logger = logging.getLogger(__name__)
pyautogui.FAILSAFE = True

class VisionSystem:
    """Система компьютерного зрения для анализа экрана"""
    
    def __init__(self):
        self.screen_width = 1920
        self.screen_height = 1080
        self.last_screenshot = None
    
    def capture_screen(self) -> np.ndarray:
        """Захват снимка экрана"""
        try:
            screenshot = ImageGrab.grab()
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            self.last_screenshot = frame
            return frame
        except Exception as e:
            logger.error(f"Ошибка захвата: {e}")
            return None
    
    def detect_colors(self, frame: np.ndarray, color_range: Dict):
        """Поиск объектов по цвету"""
        lower = np.array(color_range['lower'])
        upper = np.array(color_range['upper'])
        mask = cv2.inRange(frame, lower, upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        objects = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 100:
                x, y, w, h = cv2.boundingRect(cnt)
                objects.append({
                    'x': x + w//2,
                    'y': y + h//2,
                    'width': w,
                    'height': h,
                    'area': area
                })
        return mask, objects

class InputController:
    """Контроллер ввода - управление мышью и клавиатурой"""
    
    def __init__(self):
        self.speed = 0.5
        self.auto_mode = False
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5):
        """Плавное движение мыши"""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            logger.info(f"Мышь: ({x}, {y})")
        except Exception as e:
            logger.error(f"Ошибка: {e}")
    
    def click(self, x: int, y: int, button: str = 'left'):
        """Клик мышью"""
        try:
            pyautogui.click(x, y, button=button)
            logger.info(f"Клик: ({x}, {y})")
            time.sleep(0.3)
        except Exception as e:
            logger.error(f"Ошибка клика: {e}")
    
    def type_text(self, text: str):
        """Печать текста"""
        try:
            pyautogui.write(text, interval=0.05)
            logger.info(f"Напечатано: {text}")
        except Exception as e:
            logger.error(f"Ошибка печати: {e}")
    
    def press_key(self, key: str):
        """Нажатие клавиши"""
        try:
            pyautogui.press(key)
            logger.info(f"Клавиша: {key}")
            time.sleep(0.2)
        except Exception as e:
            logger.error(f"Ошибка: {e}")
    
    def open_app(self, app_path: str):
        """Открыть приложение"""
        import subprocess
        try:
            subprocess.Popen(app_path)
            logger.info(f"Открыто: {app_path}")
            time.sleep(2)
        except Exception as e:
            logger.error(f"Ошибка открытия: {e}")

class AIController:
    """Интеллектуальный контроллер"""
    
    def __init__(self):
        self.vision = VisionSystem()
        self.input = InputController()
        self.auto_mode = False
    
    def analyze_and_click(self, target_color: Dict) -> bool:
        """Анализирует экран и кликает на объект"""
        frame = self.vision.capture_screen()
        if frame is None:
            return False
        mask, objects = self.vision.detect_colors(frame, target_color)
        if objects:
            largest = max(objects, key=lambda x: x['area'])
            self.input.click(largest['x'], largest['y'])
            return True
        return False
    
    def open_and_control(self, app_path: str, actions: List[Dict]):
        """Открывает приложение и выполняет действия"""
        self.input.open_app(app_path)
        for action in actions:
            self.execute_action(action)
            time.sleep(1)
    
    def execute_action(self, action: Dict):
        """Выполняет действие"""
        action_type = action.get('type')
        if action_type == 'click':
            self.input.click(action['x'], action['y'])
        elif action_type == 'type':
            self.input.type_text(action['text'])
        elif action_type == 'key':
            self.input.press_key(action['key'])
        elif action_type == 'wait':
            time.sleep(action.get('time', 1))
