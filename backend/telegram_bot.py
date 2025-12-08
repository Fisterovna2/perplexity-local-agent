# Telegram Bot - Управление агентом через Telegram
# Полный контроль агента из мессенджера. Никакого облака, никаких организаций.

from flask import Flask, request, jsonify
import logging
from typing import Dict
import json

import logging
logger = logging.getLogger(__name__)

# ============================================================================
# TELEGRAM BOT V2 - С ДИАЛОГАМИ И ОЧЕРЕДЬЮ ЗАДАЧ
# ============================================================================

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
from datetime import datetime
from pathlib import Path

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8253285683:AAEg2_soyuwXWCXrjZTSNErjhJlAc2KOWnQ")
API_URL = "http://localhost:5000/api/v1"

# Хранилище состояний и очередь задач
user_state = {}
task_queue = {}
task_id_counter = 0

# ============================================================================
# КОМАНДЫ БОТА
# ============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    await update.message.reply_text(
        "🤖 *Perplexity Local Agent v2.0*\n\n"
        "Основные команды:\n"
        "🎮 /game <игра> - Играть в игру\n"
        "📅 /schedule <задача> - Добавить в очередь\n"
        "🧠 /think <часы> - Генератор идей\n"
        "📊 /status - Статус агента\n"
        "❓ /help - Справка",
        parse_mode="Markdown"
    )

async def game_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /game - диалог с пользователем о игре"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("Синтаксис: /game <название_игры>\nПример: /game Dota2")
        return
    
    game_name = " ".join(context.args)
    user_state[user_id] = {
        "mode": "wait_game_task",
        "game": game_name
    }
    
    await update.message.reply_text(
        f"🎮 *Игра: {game_name}*\n\n"
        f"Какую задачу выполнить?\n"
        f"(Пример: сыграй одну игру в турбо, фармить до 19:00)",
        parse_mode="Markdown"
    )

async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /schedule - добавить задачу в очередь"""
    global task_id_counter
    
    if not context.args:
        await update.message.reply_text(
            "Синтаксис:\n"
            "/schedule <задача> - обычная задача\n"
            "/schedule game:<игра> task:<задача> - игровая задача\n\n"
            "Примеры:\n"
            "/schedule сделать презентацию по истории\n"
            "/schedule game:Dota2 task:сыграй турбо 1 катку"
        )
        return
    
    full_text = " ".join(context.args)
    task_id_counter += 1
    
    # Парсим команду
    if "game:" in full_text and "task:" in full_text:
        parts = full_text.split()
        game = None
        task_text = None
        
        for part in parts:
            if part.startswith("game:"):
                game = part.replace("game:", "")
            elif part.startswith("task:"):
                task_text = part.replace("task:", "")
        
        if not game or not task_text:
            task_text = full_text
        
        task_data = {
            "id": task_id_counter,
            "type": "game",
            "game": game,
            "task": task_text,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
    else:
        task_data = {
            "id": task_id_counter,
            "type": "task",
            "text": full_text,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
    
    task_queue[task_id_counter] = task_data
    
    await update.message.reply_text(
        f"✅ Задача добавлена в очередь!\n"
        f"ID: {task_data['id']}\n"
        f"Тип: {task_data['type']}\n"
        f"Статус: pending\n\n"
        f"Всего задач в очереди: {len(task_queue)}"
    )

async def think_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /think - генератор идей на N часов"""
    user_id = update.effective_user.id
    
    if not context.args or "for" not in context.args:
        await update.message.reply_text("Синтаксис: /think for <часы>\nПример: /think for 3")
        return
    
    try:
        for_index = context.args.index("for")
        hours = int(context.args[for_index + 1])
    except (ValueError, IndexError):
        hours = 1
    
    user_state[user_id] = {
        "mode": "thinking",
        "hours": hours,
        "start_time": datetime.now()
    }
    
    await update.message.reply_text(
        f"🧠 *Включаю режим мышления на {hours} часа(ов)*\n\n"
        f"Генерирую идеи...\n"
        f"💡 Идеи будут обновляться каждый час",
        parse_mode="Markdown"
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /status - статус агента"""
    try:
        response = requests.get(f"{API_URL}/info", timeout=5)
        data = response.json()
        
        await update.message.reply_text(
            f"✅ *Статус Агента*\n\n"
            f"Agent: {data['agent']}\n"
            f"Version: {data['version']}\n"
            f"Status: {data['status']}\n"
            f"Safety: {data['safety_level']}\n"
            f"Tasks in queue: {len(task_queue)}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений для диалогов"""
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id not in user_state:
        return
    
    state = user_state[user_id]
    
    # Диалог для /game - пользователь вводит задачу для игры
    if state.get("mode") == "wait_game_task":
        global task_id_counter
        task_id_counter += 1
        game = state.get("game")
        
        task_data = {
            "id": task_id_counter,
            "type": "game",
            "game": game,
            "task": text,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        task_queue[task_id_counter] = task_data
        
        await update.message.reply_text(
            f"🚀 *Задача добавлена в очередь!*\n\n"
            f"Игра: {game}\n"
            f"Задача: {text}\n"
            f"Статус: PENDING ⏳",
            parse_mode="Markdown"
        )
        
        del user_state[user_id]

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Справка"""
    await update.message.reply_text(
        "/start - начало\n"
        "/game - играть в игру\n"
        "/schedule - добавить в очередь\n"
        "/think - генератор идей\n"
        "/status - статус агента"
    )

def main():
    """Запуск Telegram бота"""
    app = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("game", game_command))
    app.add_handler(CommandHandler("schedule", schedule_command))
    app.add_handler(CommandHandler("think", think_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # Обработчик текстовых сообщений для диалогов
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("🤖 Telegram BOT запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
