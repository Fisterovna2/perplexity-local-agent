""" 🤖 Perplexity Local Agent - GUI Launcher
Графический интерфейс для запуска агента с выбором настроек
"""

import tkinter as tk
from tkinter import ttk, messagebox
import yaml
import subprocess
import threading
from pathlib import Path
import sys

# Путь к конфигу
CONFIG_PATH = Path(__file__).parent / "config.yaml"


class AgentLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Perplexity Local Agent")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Загрузка конфига
        self.config = self.load_config()
        
        # Создание интерфейса
        self.create_ui()
        
    def load_config(self):
        """Загрузить config.yaml"""
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {}
    
    def save_config(self):
        """Сохранить config.yaml"""
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
    
    def create_ui(self):
        """Создать GUI"""
        # Заголовок
        title = tk.Label(
            self.root, 
            text="🤖 Perplexity Local Agent v3.0",
            font=("Arial", 18, "bold"),
            fg="#667eea"
        )
        title.pack(pady=20)
        
        # Фрейм настроек
        settings_frame = tk.LabelFrame(
            self.root,
            text="⚙️ Настройки",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=20
        )
        settings_frame.pack(padx=20, pady=10, fill="both")
        
        # === ВЫБОР РЕЖИМА МОЗГА ===
        tk.Label(settings_frame, text="🧠 Режим мозга:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=5)
        
        self.brain_mode_var = tk.StringVar(value=self.config.get("llm", {}).get("brain_mode", "ollama"))
        brain_modes = [
            ("🦙 Ollama (локальный)", "ollama"),
            ("🌐 API (облачный)", "api"),
            ("💬 Comet Chat (браузерный)", "comet_chat")
        ]
        
        for i, (label, value) in enumerate(brain_modes, start=1):
            rb = tk.Radiobutton(
                settings_frame,
                text=label,
                variable=self.brain_mode_var,
                value=value,
                font=("Arial", 10)
            )
            rb.grid(row=i, column=0, sticky="w", padx=20)
        
        # === ВЫБОР РЕЖИМА БЕЗОПАСНОСТИ ===
        tk.Label(settings_frame, text="🛡️ Режим безопасности:", font=("Arial", 11)).grid(row=4, column=0, sticky="w", pady=(15,5))
        
        self.safety_mode_var = tk.StringVar(value=self.config.get("modes", {}).get("active", "normal"))
        safety_modes = [
            ("✅ Normal (полный доступ)", "normal"),
            ("🎮 Fairplay (без читов)", "fairplay"),
            ("📚 Curious (ограниченный)", "curious")
        ]
        
        for i, (label, value) in enumerate(safety_modes, start=5):
            rb = tk.Radiobutton(
                settings_frame,
                text=label,
                variable=self.safety_mode_var,
                value=value,
                font=("Arial", 10)
            )
            rb.grid(row=i, column=0, sticky="w", padx=20)
        
        # === ДОПОЛНИТЕЛЬНЫЕ ОПЦИИ ===
        tk.Label(settings_frame, text="🚀 Запустить:", font=("Arial", 11)).grid(row=8, column=0, sticky="w", pady=(15,5))
        
        self.web_ui_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            settings_frame,
            text="🌐 Web UI (http://127.0.0.1:5000)",
            variable=self.web_ui_var,
            font=("Arial", 10)
        ).grid(row=9, column=0, sticky="w", padx=20)
        
        self.telegram_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            settings_frame,
            text="📱 Telegram бот",
            variable=self.telegram_var,
            font=("Arial", 10)
        ).grid(row=10, column=0, sticky="w", padx=20)
        
        # === КНОПКИ ===
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.start_button = tk.Button(
            button_frame,
            text="🚀 Запустить агента",
            font=("Arial", 12, "bold"),
            bg="#28a745",
            fg="white",
            width=20,
            height=2,
            command=self.start_agent
        )
        self.start_button.grid(row=0, column=0, padx=10)
        
        tk.Button(
            button_frame,
            text="❌ Выход",
            font=("Arial", 12),
            bg="#dc3545",
            fg="white",
            width=10,
            height=2,
            command=self.root.quit
        ).grid(row=0, column=1, padx=10)
        
        # === КОНСОЛЬ ВЫВОДА ===
        console_frame = tk.LabelFrame(
            self.root,
            text="📝 Статус",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        console_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.console = tk.Text(
            console_frame,
            height=10,
            bg="#1e1e1e",
            fg="#00ff00",
            font=("Consolas", 9),
            state="disabled"
        )
        self.console.pack(fill="both", expand=True)
        
    def log(self, message):
        """Вывод в консоль"""
        self.console.config(state="normal")
        self.console.insert("end", f"{message}\n")
        self.console.see("end")
        self.console.config(state="disabled")
    
    def start_agent(self):
        """Запустить агента"""
        # Сохранение настроек
        if "llm" not in self.config:
            self.config["llm"] = {}
        self.config["llm"]["brain_mode"] = self.brain_mode_var.get()
        
        if "modes" not in self.config:
            self.config["modes"] = {}
        self.config["modes"]["active"] = self.safety_mode_var.get()
        
        self.save_config()
        
        # Формирование команды
        brain_mode = self.brain_mode_var.get()
        safety_mode = self.safety_mode_var.get()
        
        self.log(f"🧠 Режим мозга: {brain_mode}")
        self.log(f"🛡️ Режим безопасности: {safety_mode}")
        self.log(f"⚙️ Настройки сохранены в config.yaml")
        
        # Запуск бэкенда
        args = [sys.executable, str(Path(__file__).parent / "main_entry.py")]
        
        if self.web_ui_var.get():
            args.append("--web")
            self.log("🌐 Запуск Web UI на http://127.0.0.1:5000")
        
        if self.telegram_var.get():
            args.append("--telegram")
            self.log("📱 Запуск Telegram бота")
        
        self.log(f"🚀 Команда: {' '.join(args)}")
        self.log("="*50)
        
        # Отключение кнопки
        self.start_button.config(state="disabled", text="⏳ Запускается...")
        
        # Запуск в отдельном потоке
        def run():
            try:
                process = subprocess.Popen(
                    args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                for line in process.stdout:
                    self.log(line.strip())
                
                process.wait()
                self.log("✅ Агент завершён")
            except Exception as e:
                self.log(f"❌ Ошибка: {e}")
            finally:
                self.start_button.config(state="normal", text="🚀 Запустить агента")
        
        threading.Thread(target=run, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = AgentLauncher(root)
    root.mainloop()
