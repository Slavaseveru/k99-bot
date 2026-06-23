import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash", system_instruction="Ты — персональный AI-ассистент К99. Умный, краткий, полезный. Отвечаешь на русском.")

conversations = {}

def get_chat(user_id):
    if user_id not in conversations:
        conversations[user_id] = model.start_chat(history=[])
    return conversations[user_id]

async def cmd_start(update, context):
    await update.message.reply_text("Привет! Я К99 — твой AI-ассистент 🤖\n/clear — очистить память\n/help — помощь")

async def cmd_clear(update, context):
    conversations.pop(update.effective_user.id, None)
    await update.message.reply_text("🗑 История очищена!")

async def cmd_help(update, context):
    await update.message.reply_text("/start — приветствие\n/clear — сбросить память\n/help — справка")

async def handle_message(update, context):
    user_id = update.effective_user.id
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        chat = get_chat(user_id)
        response = chat.send_message(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error("Error: %s", e)
        await update.message.reply_text("⚠️ Ошибка. Попробуй ещё раз.")

def main():
    app = ApplicationBuilder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot started. Polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
