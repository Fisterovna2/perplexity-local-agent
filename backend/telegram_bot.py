import telebot
import asyncio
import websockets.client as wsclient
import json

TELEGRAMTOKEN = "YOURTOKEN"
SERVERURI = "wslocalhost8000"

bot = telebot.TeleBot(TELEGRAMTOKEN)

async def sendcommand(text):
    async with wsclient.connect(SERVERURI) as ws:
        await ws.send(json.dumps({"type": "prompt", "prompt": text}))
        return "Команда отправлена Цифровому Человеку. Он начал работу с экраном."

@bot.message_handler(func=lambda m: True)
def echoall(message):
    try:
        response = asyncio.run(sendcommand(message.text))
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, f"Ошибка связи с агентом: {e}")

if __name__ == "__main__":
    bot.polling()
