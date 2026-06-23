import os
import logging
from google import genai
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
SYSTEM = "Ты ассистент К99. Отвечай кратко на русском."
conversations = {}

def get_history(user_id):
    return conversations.setdefault(user_id, [])

async def cmd_start(update, context):
    await update.message.reply_text("Привет! Я К99 🤖\n/clear — память\n/help — помощь")

async def cmd_clear(update, context):
    conversations.pop(update.effective_user.id, None)
    await update.message.reply_text("🗑 Очищено!")

async def cmd_help(update, context):
    await update.message.reply_text("/start /clear /help")

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
            config={"system_instruction": SYSTEM}
        )
        reply = response.text
        history.append({"role": "model", "parts": [{"text": reply}]})
        if len(history) > 20:
            conversations[user_id] = history[-20:]
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error("Error: %s", e)
        await update.message.reply_text("Ошибка, попробуй ещё раз.")

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
