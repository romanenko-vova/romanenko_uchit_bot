from dotenv import load_dotenv

import os
import asyncio

from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
)

from romanenko_uchit_bot.database.db import init_db

from romanenko_uchit_bot.handlers.handlers import start, user_progrev_callback

from romanenko_uchit_bot.static.states import PROGREV_MESSAGES, ADMIN_COMMANDS


load_dotenv()
filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)


def main():
    print("MAIN")

    application = Application.builder().token(os.getenv("TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PROGREV_MESSAGES: [
                CallbackQueryHandler(user_progrev_callback),
            ],
            ADMIN_COMMANDS: [
                CallbackQueryHandler(user_progrev_callback),
            ],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())

    main()
