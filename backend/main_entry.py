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
    print("4. ⚙️ Текущие настройки")
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

    def select_safety_mode():
            print("\n" + "="*60)
            print("🛡️ Режим безопасности")
            print("="*60)
            print("\n1. ✅ Normal (по умолчанию)")
            print("2. 🎮 Fairplay (честная игра)")
            print("3. 🧒 Curious (любопытный)")
            print("="*60)
            choice = input("\nВыбери (1/2/3): ").strip()
            modes = {'1': 'normal', '2': 'fairplay', '3': 'curious'}
            return modes.get(choice, 'normal')

    def set_safety_mode(mode: str):
            config = load_config()
            config['modes']['active'] = mode
            save_config(config)
            print(f"\n✅ Режим безопасности: {mode}\n")
    parser.add_argument('--telegram', action='store_true')
    parser.add_argument('--brain', choices=['ollama', 'api', 'comet_chat'])
        parser.add_argument('--mode', choices=['normal', 'fairplay', 'curious'], help='Safety mode')
    args = parser.parse_args()
    
    if args.brain:
        set_brain_mode(args.brain)
            if args.mode:
                        set_safety_mode(args.mode)
    elif not args.web and not args.telegram:
        mode = select_brain_mode()
        if mode:
            set_brain_mode(mode)
                    safety = select_safety_mode()
                    if safety:
                                    set_safety_mode(safety)
    
    if args.web:
        from agent import app
        app.run(host='127.0.0.1', port=5000, debug=False)
    
    if args.telegram:
        from telegram_super_agent import main as run_bot
        run_bot()

if __name__ == '__main__':
    main()
