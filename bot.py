import os
import logging
from anthropic import Anthropic
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

anthropic = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """Ты — персональный AI-ассистент К99.
Ты умный, краткий и полезный. Отвечаешь на русском языке, если не попросят иначе.
"""

conversations: dict[int, list[dict]] = {}
MAX_HISTORY = 20

def get_history(user_id: int) -> list[dict]:
    return conversations.setdefault(user_id, [])

def trim_history(user_id: int) -> None:
    h = conversations.get(user_id, [])
    if len(h) > MAX_HISTORY:
        conversations[user_id] = h[-MAX_HISTORY:]

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Я К99 — твой AI-ассистент 🤖\n\n/clear — очистить память\n/help — помощь")

async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    conversations.pop(update.effective_user.id, None)
    await update.message.reply_text("🗑 История очищена!")

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("/start — приветствие\n/clear — сбросить память\n/help — справка")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    history = get_history(user_id)
    history.append({"role": "user", "content": user_text})
    try:
        response = anthropic.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=history,
        )
        assistant_text = response.content[0].text
    except Exception as e:
        logger.error("Anthropic API error: %s", e)
        await update.message.reply_text("⚠️ Ошибка. Попробуй ещё раз.")
        history.pop()
        return
    history.append({"role": "assistant", "content": assistant_text})
    trim_history(user_id)
    await update.message.reply_text(assistant_text)

def main() -> None:
    app = ApplicationBuilder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("help", cmd_
