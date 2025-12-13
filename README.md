# 🤖 Perplexity Local Agent v3.0

**Локальный ИИ-агент с полным контролем над компьютером. Никакого облака, никаких ограничений.**

![Status](https://img.shields.io/badge/status-active-success)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.8+-376f9f)
![Version](https://img.shields.io/badge/version-3.0-brightgreen)

---

## 🎯 Что это?

**Perplexity Local Agent** — это мультифункциональный локальный ИИ-агент, который работает как **"второй человек"** на твоём компьютере:
- 🧠 **3 режима мозга**: Ollama (локальный), API (облачный), Comet Chat (браузерный)
- 🛡️ **3 режима безопасности**: Normal, Fairplay (без читов), Curious (ограниченный)
- 🎮 **Автоматизация игр**: Roblox, Dota 2, Bee Swarm Simulator
- 💻 **Полный контроль ПК**: файлы, программы, веб, API
- 📄 **Создание контента**: проекты, документы, презентации, 3D модели
- 🔒 **Максимальная безопасность**: self-protection, whitelist, подтверждения

---

## ⚡ Быстрый старт

```bash
# 1. Клонируй репозиторий
git clone https://github.com/Fisterovna2/perplexity-local-agent.git
cd perplexity-local-agent

# 2. Установи зависимости
pip install -r backend/requirements.txt

# 3. Настрой config.yaml (выбери режим мозга)
# modes.active: "normal" / "fairplay" / "curious"
# llm.brain_mode: "ollama" / "api" / "comet_chat"

# 4. Запусти
python backend/main_entry.py --web

# Открой http://127.0.0.1:5000 в браузере
```

**Или собери в один EXE:**
```bash
pip install pyinstaller
pyinstaller --onefile --name PerplexityLocalAgent backend/main_entry.py \
  --add-data "backend/config.yaml;backend" --add-data "frontend;frontend"

# Запусти
dist\PerplexityLocalAgent.exe
```

> 📖 **Полная инструкция**: [FINAL_BUILD_GUIDE.md](FINAL_BUILD_GUIDE.md)

---

## 🧠 3 режима работы мозга

### 1. 🦙 Ollama (локальный)
- ✅ Полностью оффлайн
- ✅ Не нужен интернет
- ✅ Приватность 100%
- 📦 Требует установки [Ollama](https://ollama.ai/)

```yaml
llm:
  brain_mode: "ollama"
  ollama:
    base_url: "http://127.0.0.1:11434"
    model: "llama3"
```

### 2. 🌐 API (облачный)
- ✅ Максимальная мощность
- ✅ Быстрые ответы
- 🔑 Требует API ключ
- Поддержка: Perplexity, OpenAI, Claude, Gemini

```yaml
llm:
  brain_mode: "api"
  provider: "perplexity"
```

### 3. 💬 Comet Chat (браузерный → локальный)
- 🧠 Модель работает в браузере Comet
- 💻 Агент исполняет команды локально
- 🔗 Связка через Tampermonkey скрипт
- Формат команд: `AGENT_CMD: {"command": "...", "params": {...}}`

```yaml
llm:
  brain_mode: "comet_chat"
```

---

## 🛡️ 3 режима безопасности

### Normal (по умолчанию)
```yaml
modes:
  active: "normal"
```
- Полный доступ в рамках whitelist
- Все инструменты доступны
- Подтверждения опасных действий

### Fairplay (честная игра)
```yaml
modes:
  active: "fairplay"
```
- 🚫 Запрещены читы и memory hacks
- ✅ Только vision/input для игр (клики, клавиши)
- 🎮 Честная автоматизация через скриншоты

### Curious (любопытный ребёнок)
```yaml
modes:
  active: "curious"
  curious:
    discord_allowed: false
```
- 🚫 Запрещена отправка в Discord
- 🚫 Ограничены опасные команды
- 📚 Только чтение и обучение

---

## 🎮 Возможности

### Автоматизация игр
- **Roblox**: сбор предметов, выполнение квестов
- **Dota 2**: фарм крипов, использование способностей  
- **Bee Swarm Simulator**: сбор пыльцы, улучшение пчёл

### Работа с проектами
- Генерация структуры проекта (папки, файлы, README)
- Создание кода на Python/JavaScript
- Git инициализация

### Создание документов
- Markdown файлы
- PDF отчёты
- PowerPoint презентации

### 3D моделирование
- Генерация моделей через Blender
- Экспорт в .blend/.obj

### Контроль ПК
- Vision: скриншоты, анализ экрана
- Input: управление мышью и клавиатурой
- Files: создание, редактирование, удаление
- Programs: запуск любых приложений
- Web: скрапинг, автоматизация

---

## 🔒 Безопасность

### Self-Protection
```yaml
self_protection:
  enabled: true
  critical_files:
    - "agent.py"
    - "safety.py"
    - "config.yaml"
```
Агент **не может** модифицировать свои критические файлы.

### SafetyManager.check_mode()
Каждая команда проверяется на ограничения режима перед выполнением:
- Fairplay блокирует читы
- Curious блокирует Discord и опасные действия
- Проверка категорий: `game_memory`, `cheat`, `system_critical`

### Whitelist/Blacklist
```yaml
allowed_commands:
  - python_exec
  - file_operation
  - open_program
  - blender_script
```
Блокировка опасных паттернов: `rm -rf`, `sudo`, `format`, `del /s`

### Подтверждения
```yaml
confirmation:
  enabled: true
  require_confirmation: true
```
Опасные действия требуют твоего "да".

---

## 📁 Структура проекта

```
perplexity-local-agent/
├── backend/
│   ├── agent.py                 # Flask API
│   ├── llm_selector.py          # LLM (Ollama/API/Comet)
│   ├── safety.py                # Безопасность + режимы
│   ├── memory.py                # Долгосрочная память
│   ├── planner.py               # Планирование задач
│   ├── autonomous_agent.py      # Автономное выполнение
│   ├── vision_controller.py     # Скриншоты и анализ
│   ├── input_control.py         # Мышь и клавиатура
│   ├── game_automation.py       # Автоматизация игр
│   ├── blender_3d.py            # Генерация 3D моделей
│   ├── tools_advanced.py        # Веб/API/файлы
│   ├── telegram_super_agent.py  # Telegram бот
│   ├── main_entry.py            # Точка входа для EXE
│   ├── config.yaml              # Конфигурация
│   └── requirements.txt         # Зависимости
├── frontend/
│   ├── index.html               # Web UI
│   ├── style.css
│   └── script.js
├── tampermonkey/
│   └── perplexity-bridge.js     # Comet Chat интеграция
├── FINAL_BUILD_GUIDE.md         # Инструкция по сборке
├── README.md                    # Этот файл
└── LICENSE                      # MIT License
```

---

## 🚀 API Endpoints

### POST `/api/v1/execute`
Выполнить команду с подтверждением

**Request:**
```json
{
  "command": "create_3d_model",
  "params": {"type": "sphere", "size": 10},
  "confirmed": true
}
```

**Response:**
```json
{
  "success": true,
  "result": "Model created at /models/sphere_10.blend",
  "execution_time": 2.35
}
```

### GET `/api/info`
Получить информацию о доступных инструментах

---

## 🎯 Примеры использования

### Режим 1: Ollama
```bash
# Установи Ollama
curl https://ollama.ai/install.sh | sh
ollama run llama3

# Запусти агента
python backend/main_entry.py --brain ollama --web
```

### Режим 2: API
```bash
# Добавь API ключ в config.yaml
# Запусти
python backend/main_entry.py --brain api --web
```

### Режим 3: Comet Chat
```bash
# 1. Установи Tampermonkey в браузер
# 2. Добавь скрипт из tampermonkey/perplexity-bridge.js
# 3. Запусти агента
python backend/main_entry.py --brain comet_chat --web

# 4. Открой Comet и пиши команды:
# AGENT_CMD: {"command": "openprogram", "params": {"program": "notepad"}, "confirmed": true}
```

---

## 📦 Сборка в EXE

**Полная инструкция**: [FINAL_BUILD_GUIDE.md](FINAL_BUILD_GUIDE.md)

```bash
pip install pyinstaller
pyinstaller --onefile --name PerplexityLocalAgent backend/main_entry.py \
  --add-data "backend/config.yaml;backend" \
  --add-data "frontend;frontend"

# Результат: dist/PerplexityLocalAgent.exe
```

**Запуск:**
```bash
# Интерактивное меню
PerplexityLocalAgent.exe

# Быстрый запуск
PerplexityLocalAgent.exe --brain ollama --web
PerplexityLocalAgent.exe --brain comet_chat --web --telegram
```

---

## 🤝 Contributing

Пулл-реквесты приветствуются! Для крупных изменений сначала открой issue.

---

## 📄 License

MIT License - делай что хочешь.

---

## ⚠️ Disclaimer

Используй на свой страх и риск. Автоматизация игр может нарушать ToS. Fairplay режим рекомендуется для честной игры.

---

## 🔗 Links

- [FINAL_BUILD_GUIDE.md](FINAL_BUILD_GUIDE.md) — Полная инструкция по сборке
- [Ollama](https://ollama.ai/) — Локальные LLM
- [Perplexity](https://perplexity.ai/) — Облачный API

---

**Made with ❤️ for automation enthusiasts**
