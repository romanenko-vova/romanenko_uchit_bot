from dotenv import load_dotenv

import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


load_dotenv()


async def check_subscription(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user_id = update.message.from_user.id

    channel_id = "@romanenko_uchit"

    try:
        # Get the chat member status
        member = await context.bot.get_chat_member(chat_id=channel_id, user_id=user_id)

        if member.status in ["member", "administrator", "creator"]:
            await update.message.reply_text("You are subscribed to the channel!")
        else:
            await update.message.reply_text("You are not subscribed to the channel.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")


def main():
    print("MAIN")

    application = Application.builder().token(os.getenv("TOKEN")).build()

    check_subscription_handler = CommandHandler("start", check_subscription)
    application.add_handler(check_subscription_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
