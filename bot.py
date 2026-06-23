import os
import logging
from google import genai
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

conversations = {}

def get_history(user_id):
    return conversations.setdefault(user_id, [])

async def cmd_start(update, context):
    await update.message.reply_text("Привет! Я К99 🤖\n/clear — очистить память\n/help — помощь")

async def cmd_clear(update, context):
    conversations.pop(update.effective_user.id, None)
    await update.message.reply_text("🗑 История очищена!")

async def cmd_help(update, context):
    await update.message.reply_text("/start — приветствие\n/clear — память\n/help — справка")

async def handle_message(update, context):
    user_id = update.effective_user.id
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    history = get_history(user_id)
    history.append({"role": "user", "parts": [{"text": user_text}]})
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=history,
            config={"system_instruction": "Ты — персональный AI-ассистент К99. Умный, краткий, полезный. Отвечаешь на рус
