from telegram.ext import (
    ContextTypes,
)

from romanenko_uchit_bot.static.ids import GROUP_ID

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from romanenko_uchit_bot.static.callbacks import GETTING_GUIDE, FREE_LESSON
from romanenko_uchit_bot.static.keys import GROUP_MESSAGE, USERNAME, FIRST_MSG

(ONCE_WAY_IT_JOB, GROUP_MSG, FREE_LSN) = range(3)


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


async def free_lesson_job(context: ContextTypes.DEFAULT_TYPE) -> int:
    job = context.job

    keyboard = [
        [
            InlineKeyboardButton("Получить бесплатный урок", callback_data=FREE_LESSON),
        ],
    ]

    await context.bot.send_message(
        chat_id=job.chat_id,
        text="Заинтересовало?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def group_msg_job(context: ContextTypes.DEFAULT_TYPE) -> int:
    if (
        GROUP_MESSAGE in context.job.data
        and USERNAME in context.job.data[GROUP_MESSAGE]
        and context.job.data[GROUP_MESSAGE][USERNAME]
    ):
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=context.job.data[GROUP_MESSAGE][USERNAME],
        )

    else:
        job = context.job

        await context.bot.forwardMessage(
            chat_id=GROUP_ID,
            from_chat_id=job.chat_id,
            message_id=context.job.data[GROUP_MESSAGE][FIRST_MSG],
        )
