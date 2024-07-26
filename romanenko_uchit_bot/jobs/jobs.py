from telegram.ext import (
    ContextTypes,
)

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from romanenko_uchit_bot.static.callbacks import GETTING_GUIDE

(ONCE_WAY_IT_JOB,) = range(1)


async def way_to_it_job(context: ContextTypes.DEFAULT_TYPE) -> int:
    job = context.job

    keyboard = [
        [
            InlineKeyboardButton("Получить Гайд", callback_data=GETTING_GUIDE),
        ],
    ]

    await context.bot.send_message(
        chat_id=job.chat_id,
        text="Путь в IT",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
