from telegram.ext import (
    ContextTypes,
)

from telegram.constants import ParseMode

from romanenko_uchit_bot.static.ids import GROUP_ID
from romanenko_uchit_bot.static.strings import GUIDE_GROUP, FREE_LESSON_MESAGE

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from romanenko_uchit_bot.tools.escape_text import escape_text

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
        text=escape_text(FREE_LESSON_MESAGE),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def group_msg_job(context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=GUIDE_GROUP,
    )

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


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)

    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()

    return True
