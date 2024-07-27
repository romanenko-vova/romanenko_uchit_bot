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
    MessageHandler,
    filters,
)

from romanenko_uchit_bot.database.db import init_db

from romanenko_uchit_bot.handlers.handlers import (
    start,
    user_progrev_callback,
    admin_callbacks,
    save_phone,
    get_mail,
)

from romanenko_uchit_bot.static.states import (
    PROGREV_MESSAGES,
    ADMIN_COMMANDS,
    PHONE,
    GET_MAIL,
)


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
                CallbackQueryHandler(admin_callbacks),
            ],
            GET_MAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_mail)],
            PHONE: [MessageHandler(filters.CONTACT, save_phone)],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())

    main()
