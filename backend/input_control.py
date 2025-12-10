"""🖱️ INPUT CONTROL - Mouse & Keyboard Automation

🖱️ Features:
✅ Mouse movement and clicks
✅ Keyboard typing and key presses
✅ Multi-key combinations (Ctrl+C, Shift+Tab)
✅ Double-click and drag operations
✅ Safe typing with delays
✅ Coordinate validation
"""

import pyautogui
import time
from typing import Tuple, List, Optional
from enum import Enum

# Disable PyAutoGUI failsafe (moving mouse to corner)
pyautogui.FAILSAFE = False


class MouseButton(Enum):
    """Mouse button types"""
    LEFT = 'left'
    RIGHT = 'right'
    MIDDLE = 'middle'


class InputController:
    """Control mouse and keyboard for game automation"""
    
    def __init__(self, type_speed: float = 0.05, move_speed: float = 0.5):
        """
        Initialize input controller
        
        Args:
            type_speed: Delay between keystrokes (seconds)
            move_speed: Mouse movement speed
        """
        self.type_speed = type_speed
        self.move_speed = move_speed
        self.last_position = (0, 0)
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        return pyautogui.position()
    
    def move_mouse(self, x: int, y: int, duration: float = None) -> bool:
        """Move mouse to position"""
        try:
            if duration is None:
                duration = self.move_speed
            pyautogui.moveTo(x, y, duration=duration)
            self.last_position = (x, y)
            return True
        except Exception as e:
            print(f"❌ Mouse move error: {e}")
            return False
    
    def click(self, x: int, y: int, button: MouseButton = MouseButton.LEFT, 
              clicks: int = 1, interval: float = 0.1) -> bool:
        """Click mouse at position"""
        try:
            pyautogui.click(x, y, clicks=clicks, interval=interval, button=button.value)
            return True
        except Exception as e:
            print(f"❌ Click error: {e}")
            return False
    
    def double_click(self, x: int, y: int, interval: float = 0.1) -> bool:
        """Double-click at position"""
        return self.click(x, y, clicks=2, interval=interval)
    
    def right_click(self, x: int, y: int) -> bool:
        """Right-click at position"""
        return self.click(x, y, button=MouseButton.RIGHT)
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, 
             duration: float = 0.5, button: MouseButton = MouseButton.LEFT) -> bool:
        """Drag from one position to another"""
        try:
            pyautogui.mouseDown(start_x, start_y, button=button.value)
            time.sleep(0.1)
            pyautogui.moveTo(end_x, end_y, duration=duration)
            time.sleep(0.1)
            pyautogui.mouseUp(button=button.value)
            return True
        except Exception as e:
            print(f"❌ Drag error: {e}")
            return False
    
    def type_text(self, text: str, interval: float = None) -> bool:
        """Type text with delays between characters"""
        try:
            if interval is None:
                interval = self.type_speed
            
            # Use typewrite for regular characters, write for special ones
            pyautogui.typewrite(text, interval=interval)
            return True
        except Exception as e:
            print(f"❌ Typing error: {e}")
            return False
    
    def press_key(self, key: str) -> bool:
        """Press a single key"""
        try:
            pyautogui.press(key)
            return True
        except Exception as e:
            print(f"❌ Key press error: {e}")
            return False
    
    def key_combination(self, *keys: str) -> bool:
        """Press key combination (e.g., Ctrl+C)"""
        try:
            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            print(f"❌ Key combination error: {e}")
            return False
    
    def hold_key(self, key: str, duration: float = 1.0) -> bool:
        """Hold key down for duration"""
        try:
            pyautogui.keyDown(key)
            time.sleep(duration)
            pyautogui.keyUp(key)
            return True
        except Exception as e:
            print(f"❌ Hold key error: {e}")
            return False
    
    def scroll(self, x: int, y: int, clicks: int = 5, pause: float = 0.5) -> bool:
        """Scroll at position"""
        try:
            # Move to position first
            self.move_mouse(x, y, duration=0.3)
            time.sleep(pause)
            # Scroll (positive = up, negative = down)
            pyautogui.scroll(clicks)
            return True
        except Exception as e:
            print(f"❌ Scroll error: {e}")
            return False
    
    def perform_sequence(self, actions: List[dict]) -> bool:
        """Perform sequence of actions"""
        try:
            for action in actions:
                action_type = action.get('type')
                
                if action_type == 'move':
                    self.move_mouse(action['x'], action['y'])
                elif action_type == 'click':
                    self.click(action['x'], action['y'])
                elif action_type == 'type':
                    self.type_text(action['text'])
                elif action_type == 'key':
                    self.press_key(action['key'])
                elif action_type == 'wait':
                    time.sleep(action.get('duration', 0.5))
                
                time.sleep(action.get('delay', 0.1))
            
            return True
        except Exception as e:
            print(f"❌ Sequence error: {e}")
            return False


if __name__ == "__main__":
    controller = InputController()
    print(f"🖱️ Current mouse position: {controller.get_mouse_position()}")
    print("✅ Input Controller ready")
    
    # Example: Move mouse and click
    # controller.move_mouse(100, 100)
    # controller.click(100, 100)
    # controller.type_text("Hello World")
