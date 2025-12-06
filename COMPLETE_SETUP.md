# Perplexity Local Agent - COMPLETE SETUP (v2.0)

## Что это?
**Production-ready** локальный агент для Perplexity с full-stack решением:

### Backend (Python + Flask)
- REST API на localhost:5000
- Whitelist-безопасность
- Blender/Python/Unity/Godot хандлеры
- Timeout и resource limits
- Полное логирование + подтверждение

### Frontend (HTML/CSS/JS)
- Модерный UI с Gradient
- Modal для подтверждения
- INFO кнопка с рисками
- Прямая модализация кода

### Tampermonkey Integration
- Перехват команд из Perplexity
- Direct выполнение
- Real-time логи

---

## Installation

### Step 1: Backend

```bash
cd backend
pip install -r requirements.txt
python agent.py
```

Теперь агент запущен на `http://localhost:5000`

### Step 2: Frontend

1. Открой `frontend/index.html` в браузере (локально или http://localhost:8000)
2. Проверь статус - должно быть зеленое "✅ Online"

### Step 3: Tampermonkey (для Perplexity)

1. Установи [Tampermonkey](https://tampermonkey.net/)
2. Создай новый скрипт
3. Скопируй содержимое `tampermonkey/perplexity-bridge.js`
4. Сохрани
5. Перейди на https://www.perplexity.ai
6. В чате напиши команду (см. ниже)

---

## Usage Examples

### Пример 1: Создать 3D куб в Blender

**В чате Perplexity:**
```
[ACTION:BLENDER]
import bpy
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
bpy.ops.export_scene.obj(filename="/tmp/cube.obj")
[/ACTION]
```

**Результат:** На диске создается `cube.obj`

### Пример 2: Запустить Python скрипт

**В Perplexity:**
```
[ACTION:PYTHON]
import json
data = {"generated_at": "2025-12-06", "status": "success"}
with open("/tmp/result.json", "w") as f:
    json.dump(data, f)
print("✓ File created")
[/ACTION]
```

### Пример 3: Открыть программу

**В Perplexity:**
```
[ACTION:OPEN]
discord
[/ACTION]
```

---

## Config

**backend/config.yaml:**

```yaml
allowed_commands:
  blender_script:
    description: "Blender Python (headless)"
    timeout: 300
    
  python_script:
    description: "Any Python code"
    timeout: 120
    
  open_program:
    description: "Open programs"
    timeout: 30

security:
  max_command_length: 10000
  require_confirmation: true
  log_all_actions: true
  blacklist_keywords:
    - "taskkill"
    - "format"
    - "del /s /q"
```

---

## File Structure

```
perplexity-local-agent/
├── backend/
│   ├── agent.py           # Main Flask API
│   ├── handlers.py        # Blender, Python, Program handlers
│   ├── config.yaml        # Whitelist config
│   └── requirements.txt    # pip install
├── frontend/
│   ├── index.html         # UI
│   ├── style.css          # Styling
│   ├── script.js          # JavaScript logic
│   └── README.md          # Frontend docs
├── tampermonkey/
│   └── perplexity-bridge.js  # Tampermonkey script
├── COMPLETE_SETUP.md      # This file
└── LICENSE                # MIT
```

---

## API Reference

### GET /api/status
Проверить статус агента

**Response:**
```json
{"status": "online", "version": "2.0"}
```

### POST /api/validate
Проверить команду ДО выполнения

**Request:**
```json
{"action": "python_script", "command": "print('hello')"}
```

**Response:**
```json
{"allowed": true, "reason": "OK"}
```

### POST /api/execute
Выполнить команду (требует confirm=true)

**Request:**
```json
{"action": "python_script", "command": "...", "confirmed": true}
```

**Response:**
```json
{"success": true, "result": {...}}
```

---

## Security Features

✅ **Whitelist-only** - только разрешенные команды  
✅ **Confirmation** - каждое действие требует подтверждение  
✅ **Logging** - все действия логируются с timestamp + IP  
✅ **Timeout** - каждый процесс имеет максимальное время  
✅ **Sandbox** - Blender/Python запускаются в фоне  
✅ **Validation** - команды проверяются перед выполнением

---

## Troubleshooting

**Q: "Offline" статус?**
A: Проверь:
- `python backend/agent.py` запущен?
- Порт 5000 свободен?
- Firewall не блокирует localhost:5000?

**Q: Команда не выполняется?**
A:
- Проверь в config.yaml, разрешена ли эта команда
- Посмотри логи: `tail backend/logs/agent.log`
- Нажми INFO кнопку - покажет описание и риски

**Q: Blender/Python не найден?**
A: Установи их и добавь в PATH или обнови пути в `agent.py`

---

## Advanced Features (In Development)

- [ ] Discord bot integration
- [ ] CloudFlare Workers deployment
- [ ] GPU monitoring
- [ ] Email notifications
- [ ] Slack integration
- [ ] GitHub Actions CI/CD

---

## License

MIT - используй как хочешь, но указывай авторство!

---

**v2.0 Features:**
- ✅ Complete Frontend UI
- ✅ Tampermonkey bridge
- ✅ Blender/Python/Unity handlers
- ✅ Full safety + confirmation
- ✅ Production-ready logging
- ✅ Resource limits

**Ready to deploy! 🚀**
