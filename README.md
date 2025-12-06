# 🤖 Perplexity Local Agent

**Локальный ИИ-агент с полным контролем. Никакого облака, никаких ограничений.**

![Status](https://img.shields.io/badge/status-active-success)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.8+-3776ab)
![Version](https://img.shields.io/badge/version-2.0-brightgreen)

---

## 🎯 Суть проекта

**Perplexity Local Agent** — это полнофункциональный локальный ИИ-агент, который работает на твоей машине **без интернета** и **без облачных сервисов**. Это приватная альтернатива Perplexity AI с полным контролем над данными и функциональностью.

### Ключевые возможности:
- ✅ **100% локально** — ничего не отправляется в облако
- ✅ **Модульная архитектура** — легко добавлять свои инструменты
- ✅ **Максимум безопасности** — подтверждение перед каждым действием + INFO кнопка
- ✅ **REST API** — интегрируется с чем угодно
- ✅ **Web UI + Tampermonkey** — браузерный интерфейс + интеграция в Perplexity
- ✅ **Python инструменты** — создание 3D моделей, игр, автоматизация

---

## 🚀 Быстрый старт

### 1️⃣ Требования
```bash
Python 3.8+
Flask
Олучательно: Ollama или LM Studio (для локальных LLM)
```

### 2️⃣ Установка
```bash
git clone https://github.com/Fisterovna2/perplexity-local-agent
cd perplexity-local-agent
pip install -r backend/requirements.txt
```

### 3️⃣ Запуск
```bash
./run.sh
```

Агент будет доступен на **http://localhost:5000**

### 4️⃣ Использование
- **Web UI**: http://localhost:5000
- **REST API**: `http://localhost:5000/api/execute`
- **Tampermonkey**: установи скрипт из `tampermonkey/perplexity-bridge.js`

---

## 📋 Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│  (Web UI + Tampermonkey Integration)                        │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP REST API
                   ↓
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND (Flask)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ API Router (auth + whitelist + validation)          │  │
│  └────────────────┬─────────────────────────────────────┘  │
│                   │                                         │
│  ┌────────────────▼──────────────────────────────────────┐ │
│  │ Execution Engine (confirmation + safety checks)     │ │
│  └────────────────┬──────────────────────────────────────┘ │
│                   │                                         │
│  ┌────────────────▼──────────────────────────────────────┐ │
│  │ Tool Modules:                                        │ │
│  │ • Python Script Executor (sandbox)                   │ │
│  │ • File Operations                                    │ │
│  │ • Program Launcher                                   │ │
│  │ • Blender Integration                                │ │
│  │ • Custom Tools (extendable)                          │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
│  Config: config.yaml (whitelist + settings)               │
│  Logs: logs/agent.log                                      │
└─────────────────────────────────────────────────────────────┘
     │
     └─→ OS Commands / Files / External Programs / LLM
```

---

## 📦 Структура проекта

```
perplexity-local-agent/
├── backend/
│   ├── agent.py              # Основная Flask приложение
│   ├── config.yaml           # Настройки и whitelist команд
│   ├── requirements.txt       # Python зависимости
│   └── logs/                 # Логи выполнения
├── frontend/
│   ├── index.html            # Web интерфейс
│   ├── style.css             # Стили
│   └── script.js             # Логика клиента
├── tampermonkey/
│   └── perplexity-bridge.js  # Скрипт для Perplexity.ai
├── run.sh                    # Startup скрипт (one-click)
├── README.md                 # Этот файл
├── SETUP_GUIDE.md            # Пошаговая установка
├── COMPLETE_SETUP.md         # Полная конфигурация
├── RELEASE_NOTES.md          # История релизов
├── LICENSE                   # MIT License
└── .gitignore               # Git исключения
```

---

## 🔌 API Endpoints

### POST `/api/execute`
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

```json
{
  "tools": [
    {"name": "python_exec", "description": "Execute Python code safely"},
    {"name": "create_3d_model", "description": "Create 3D model using Blender"},
    {"name": "file_operation", "description": "Create/read/write files"}
  ],
  "safety_level": "MAXIMUM",
  "requires_confirmation": true
}
```

---

## ⚙️ Конфигурация

### `config.yaml` — белый список команд

```yaml
whitelist:
  allowed_commands:
    - "python_exec"
    - "file_operation"
    - "open_program"
    - "create_3d_model"
  
  blocked_patterns:
    - "rm -rf"
    - "format"
    - "sudo"

safety:
  require_confirmation: true  # Подтверждение перед действием
  require_info: true          # INFO кнопка с описанием
  sandbox_python: true        # Безопасное исполнение Python
  max_execution_time: 30      # Таймаут в секундах
```

---

## 🛠️ Использование инструментов

### 1. Python Script Executor (Sandbox)
```python
# Frontend request
{
  "command": "python_exec",
  "code": "import requests; print(requests.get('https://api.example.com').json())"
}

# Выполнится в защищённой среде с ограничениями
```

### 2. 3D Model Creation (Blender)
```python
{
  "command": "create_3d_model",
  "type": "sphere",
  "parameters": {"radius": 5, "material": "metal"}
}
```

### 3. File Operations
```python
{
  "command": "file_operation",
  "action": "create",
  "path": "/home/user/projects/file.txt",
  "content": "Hello World"
}
```

---

## 🔒 Безопасность

### Уровни защиты:
1. **Whitelist команд** — только одобренные действия
2. **Confirmation dialogs** — пользователь одобряет каждое действие
3. **INFO button** — точное описание что будет сделано
4. **Python Sandbox** — изолированное выполнение кода
5. **Таймауты** — максимальное время выполнения
6. **Логирование** — все действия логируются

---

## 📊 Примеры использования

### Пример 1: Создать Python скрипт
```bash
curl -X POST http://localhost:5000/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "file_operation",
    "action": "create",
    "path": "script.py",
    "content": "print(\"Hello\")",
    "confirmed": true
  }'
```

### Пример 2: Web UI
1. Открыть http://localhost:5000
2. Ввести команду в поле
3. Нажать INFO для описания
4. Нажать Send для выполнения

### Пример 3: Perplexity Integration
1. Установить Tampermonkey
2. Добавить скрипт из `tampermonkey/perplexity-bridge.js`
3. На Perplexity.ai появится кнопка "Local Agent"
4. Отправлять команды прямо из чата Perplexity

---

## 🚦 Roadmap v2.1+

- [ ] **LLM Integration** — интеграция с Ollama/LM Studio для умных команд
- [ ] **Plugin System** — официальный API для своих инструментов
- [ ] **Web Dashboard** — улучшенный UI с статистикой
- [ ] **Docker Support** — one-click Docker контейнер
- [ ] **Encryption** — зашифрованная история команд
- [ ] **Multi-user** — поддержка нескольких пользователей
- [ ] **Advanced Logging** — детальные логи всех действий
- [ ] **Performance Monitoring** — мониторинг нагрузки
- [ ] **Cloud Sync** — опциональная синхронизация (end-to-end encrypted)

---

## 🤝 Контрибьютинг

Хочешь добавить свой инструмент? Просто:

1. Форкни репо
2. Создай ветку: `git checkout -b feature/my-tool`
3. Добавь свой tool модуль в `backend/`
4. Тестируй
5. Отправь Pull Request

---

## 📝 Лицензия

MIT License — используй, модифицируй, распространяй свободно.

Полный текст: [LICENSE](LICENSE)

---

## 🙋 Поддержка

- 📖 **Документация**: см. `SETUP_GUIDE.md` и `COMPLETE_SETUP.md`
- 🐛 **Баги**: открой Issue
- 💡 **Идеи**: открой Discussion
- 📧 **Контакт**: создатель Fisterovna2

---

## ⭐ Если нравится — звёздочку!

```
█ █ █ █ █
█ █ █ █ █  ← Твоя звезда сюда! (кнопка наверху справа)
█ █ █ █ █
```

---

**Создано с ❤️ для локального AI контроля**

_"Данные — твои. Вычисления — твои. Контроль — твой."_
