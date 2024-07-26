from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message.id
    await context.bot.forwardMessage(chat_id=-4270539079, from_chat_id=update.effective_chat.id, message_id=message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )
