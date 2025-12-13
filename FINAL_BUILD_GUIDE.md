# 🚀 FINAL BUILD GUIDE

## Финальная сборка Perplexity Local Agent v3.0

### ✅ Что уже готово

1. **Config.yaml** — добавлены режимы (normal/fairplay/curious) и LLM конфигурация (ollama/api/comet_chat)
2. **Safety.py** — добавлен метод `SafetyManager.check_mode()` для проверки ограничений режимов
3. **Все модули** — LLM selector, Memory, Planner, Vision, Input Control, Game Automation, Blender 3D, Tools Advanced

### 🔧 Что осталось доделать вручную

#### 1. Добавить вызов check_mode в backend/agent.py

Найди функцию `execute_command()` (примерно строка 215) и добавь после проверки whitelist:

```python
# Проверка режима
from safety import SafetyManager
allowed, msg = SafetyManager.check_mode(
    command=data.get('command'),
    category=data.get('category', ''),
    target=data.get('target', '')
)
if not allowed:
    return jsonify({'success': False, 'error': msg, 'reason': 'mode_restricted'}), 403
```

#### 2. Добавить Ollama и CometChat коннекторы в backend/llm_selector.py

Добавь в конец файла перед функцией `get_llm()`:

```python
class OllamaConnector:
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip('/')
        self.model = model

    def generate(self, prompt: str, system: str = '', history: list = None) -> str:
        import requests
        payload = {
            'model': self.model,
            'messages': []
        }
        if system:
            payload['messages'].append({'role': 'system', 'content': system})
        if history:
            payload['messages'].extend(history)
        payload['messages'].append({'role': 'user', 'content': prompt})
        
        r = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=60)
        r.raise_for_status()
        return r.json().get('message', {}).get('content', '')

class CometChatConnector:
    def __init__(self):
        pass
    
    def generate(self, prompt: str, system: str = '', history: list = None) -> str:
        return '⚠️ Comet Chat Mode: команды приходят через Tampermonkey'
```

И в функции `get_llm()` добавь:

```python
if brain_mode == 'ollama':
    return OllamaConnector(
        base_url=config['llm']['ollama']['base_url'],
        model=config['llm']['ollama']['model']
    )

if brain_mode == 'comet_chat':
    return CometChatConnector()
```

#### 3. Обновить tampermonkey/perplexity-bridge.js

Добавь в конец файла:

```javascript
// === РЕЖИМ 3: Comet Chat Bridge ===
const AGENT_API = 'http://127.0.0.1:5000/apiv1/execute';

function parseAgentCommand(text) {
    const match = text.match(/AGENT_CMD:\s*(\{[\s\S]*?\})/);
    if (match) {
        try {
            return JSON.parse(match[1]);
        } catch (e) {
            return null;
        }
    }
    return null;
}

async function sendToLocalAgent(cmdData) {
    const response = await fetch(AGENT_API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            source: 'comet_chat',
            command: cmdData.command,
            params: cmdData.params || {},
            category: cmdData.category || '',
            confirmed: cmdData.confirmed || false
        })
    });
    return response.json();
}

function observeCometMessages() {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1) {
                    const cmd = parseAgentCommand(node.textContent);
                    if (cmd) {
                        sendToLocalAgent(cmd);
                    }
                }
            });
        });
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
}

if (window.location.href.includes('perplexity.ai')) {
    setTimeout(observeCometMessages, 2000);
}
```

#### 4. Создать backend/main_entry.py

Создай новый файл `backend/main_entry.py`:

```python
import argparse
import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / 'config.yaml'

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_config(config):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True)

def select_brain_mode():
    print("\n" + "="*60)
    print("🧠 PERPLEXITY LOCAL AGENT - Выбор режима")
    print("="*60)
    print("\n1. 🦙 Ollama (локальный)")
    print("2. 🌐 API (облачный)")
    print("3. 💬 Comet Chat (браузерный)")
    print("4. ⚙️  Текущие настройки")
    print("="*60)
    
    choice = input("\nВыбери (1/2/3/4): ").strip()
    modes = {'1': 'ollama', '2': 'api', '3': 'comet_chat', '4': None}
    return modes.get(choice)

def set_brain_mode(mode: str):
    config = load_config()
    config['llm']['brain_mode'] = mode
    save_config(config)
    print(f"\n✅ Режим: {mode}\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--web', action='store_true')
    parser.add_argument('--telegram', action='store_true')
    parser.add_argument('--brain', choices=['ollama', 'api', 'comet_chat'])
    args = parser.parse_args()

    if args.brain:
        set_brain_mode(args.brain)
    elif not args.web and not args.telegram:
        mode = select_brain_mode()
        if mode:
            set_brain_mode(mode)
    
    if args.web:
        from agent import app
        app.run(host='127.0.0.1', port=5000, debug=False)
    
    if args.telegram:
        from telegram_super_agent import main as run_bot
        run_bot()

if __name__ == '__main__':
    main()
```

---

## 🎯 Сборка EXE

### Шаг 1: Установка зависимостей

```bash
pip install -r backend/requirements.txt
pip install pyinstaller
```

### Шаг 2: Сборка

```bash
pyinstaller --onefile --name PerplexityLocalAgent backend/main_entry.py --add-data "backend/config.yaml;backend" --add-data "frontend;frontend"
```

### Шаг 3: Запуск

#### Интерактивное меню:
```bash
dist\PerplexityLocalAgent.exe
```

#### Быстрый запуск:
```bash
# Ollama + Web UI
dist\PerplexityLocalAgent.exe --brain ollama --web

# Comet Chat + Web UI + Telegram
dist\PerplexityLocalAgent.exe --brain comet_chat --web --telegram

# API режим
dist\PerplexityLocalAgent.exe --brain api --web
```

---

## 📝 Как использовать

### Режим 1: Ollama (локальный мозг)
1. Установи Ollama: https://ollama.ai/
2. Запусти модель: `ollama run llama3`
3. В config.yaml установи `brain_mode: ollama`
4. Запусти агента

### Режим 2: API (облачный мозг)
1. В config.yaml установи `brain_mode: api`
2. Настрой provider (perplexity/openai/claude)
3. Добавь API ключи
4. Запусти агента

### Режим 3: Comet Chat (браузерный мозг)
1. В config.yaml установи `brain_mode: comet_chat`
2. Установи Tampermonkey скрипт в браузере
3. Запусти агента с `--web`
4. Открой Comet в браузере
5. Пиши команды в формате:
   ```
   AGENT_CMD: {"command": "openprogram", "params": {"program": "notepad"}, "confirmed": true}
   ```

---

## 🛡️ Режимы безопасности

### Normal (по умолчанию)
- Полный доступ в рамках whitelist
- Все инструменты доступны

### Fairplay (честная игра)
В config.yaml:
```yaml
modes:
  active: "fairplay"
```
- Запрещены читы и memory hacks
- Только vision/input для игр

### Curious (любопытный ребёнок)
В config.yaml:
```yaml
modes:
  active: "curious"
```
- Запрещена отправка в Discord
- Ограничены опасные команды
- Только чтение и обучение

---

## ✅ Проект завершён!

Теперь у тебя есть:
- ✅ 3 режима мозга (Ollama/API/Comet)
- ✅ 3 режима безопасности (Normal/Fairplay/Curious)
- ✅ Защита от саморедактирования
- ✅ Один EXE файл
- ✅ Полная автоматизация ПК и игр
- ✅ Поддержка проектов, документов, презентаций

Удачи! 🚀
