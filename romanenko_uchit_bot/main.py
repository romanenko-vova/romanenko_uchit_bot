from dotenv import load_dotenv

import os
import asyncio

from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
)

from romanenko_uchit_bot.database.db import init_db
from romanenko_uchit_bot.handlers.handlers import start

load_dotenv()


def main():
    print("MAIN")

    application = Application.builder().token(os.getenv("TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={},
        fallbacks=[],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())

    main()
