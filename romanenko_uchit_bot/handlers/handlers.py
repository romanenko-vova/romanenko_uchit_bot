from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

import aiosqlite

from romanenko_uchit_bot.static.ids import ADMINS, GROUP_ID
from romanenko_uchit_bot.static.conversions import (
    CONV_REGISTERED,
    CONV_GUIDE,
    CONV_PHONE,
    CONV_HELPER,
)
from romanenko_uchit_bot.static.states import PROGREV_MESSAGES, ADMIN_COMMANDS, PHONE
from romanenko_uchit_bot.static.callbacks import (
    CONVERSIONS,
    LEADER_BOARD,
    MAIL,
    GETTING_GUIDE,
    FREE_LESSON,
)
from romanenko_uchit_bot.static.keys import GROUP_MESSAGE, USERNAME, FIRST_MSG
from romanenko_uchit_bot.static.time import (
    WAY_TO_IT_TIME,
    GROUP_MSG_TIME,
    FREE_LESSON_TIME,
)

from romanenko_uchit_bot.database.db import DB_PATH

from romanenko_uchit_bot.tools.escape_text import escape_text

from romanenko_uchit_bot.jobs.jobs import (
    way_to_it_job,
    group_msg_job,
    free_lesson_job,
    remove_job_if_exists,
    ONCE_WAY_IT_JOB,
    GROUP_MSG,
    FREE_LSN,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id

    if update.effective_user.id in ADMINS:
        """ Open Admin Panel """

        keyboard = [
            [
                InlineKeyboardButton("Конверсии", callback_data=CONVERSIONS),
                InlineKeyboardButton(
                    "Список Пользователей", callback_data=LEADER_BOARD
                ),
            ],
            [
                InlineKeyboardButton("Отправить рассылку", callback_data=MAIL),
            ],
        ]

        await context.bot.send_message(
            chat_id=user_id,
            text=escape_text("Hey! You are in *Admin Panel*"),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

        return ADMIN_COMMANDS

    else:
        """ save if user don't have username """
        context.user_data[GROUP_MESSAGE] = {
            FIRST_MSG: update.effective_message.id,
        }

        """ Register User """
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT name FROM users WHERE id_tg = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    await db.execute(
                        """
                        INSERT INTO users (id_tg, status, name) 
                        VALUES (?, ?, ?)
                    """,
                        (
                            user_id,
                            CONV_REGISTERED,
                            f"{update.effective_user.first_name} {update.effective_user.last_name}",
                        ),
                    )

                await db.commit()

        with open("romanenko_uchit_bot/img/me.JPG", "rb") as f:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=f,
                caption=escape_text(
                    "*Я могу помочь вашему ребенку стать программистом*"
                ),
                parse_mode=ParseMode.MARKDOWN_V2,
            )

        context.job_queue.run_once(
            way_to_it_job,
            WAY_TO_IT_TIME,
            chat_id=user_id,
            name=f"{user_id}-{ONCE_WAY_IT_JOB}",
        )

        return PROGREV_MESSAGES


async def user_progrev_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    user_id = update.effective_chat.id

    await context.bot.delete_message(
        chat_id=user_id,
        message_id=update.effective_message.message_id,
    )

    if int(query.data) == GETTING_GUIDE:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                    UPDATE users
                    SET status = ?
                    WHERE id_tg = ?
                """,
                (CONV_GUIDE, user_id),
            )

            await db.commit()

        await context.bot.send_message(
            chat_id=user_id,
            text=escape_text("*Гайд*"),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

        context.job_queue.run_once(
            group_msg_job,
            GROUP_MSG_TIME,
            chat_id=user_id,
            name=f"{user_id}-{GROUP_MSG}",
            data={
                GROUP_MESSAGE: {
                    FIRST_MSG: context.user_data[GROUP_MESSAGE][FIRST_MSG],
                    USERNAME: update.effective_user.name
                    if "@" in update.effective_user.name
                    else None,
                }
            },
        )

        """ request in 30 min to the lesson"""

        context.job_queue.run_once(
            free_lesson_job,
            FREE_LESSON_TIME,
            chat_id=user_id,
            name=f"{user_id}-{FREE_LSN}",
        )

        return PROGREV_MESSAGES

    elif int(query.data) == FREE_LESSON:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                    UPDATE users
                    SET status = ?
                    WHERE id_tg = ?
                """,
                (CONV_PHONE, user_id),
            )

            await db.commit()

        keyboard = [[KeyboardButton("Отправить контакт", request_contact=True)]]

        await context.bot.send_message(
            chat_id=user_id,
            text="Поделитесь контактом и с Вами свяжется моя помощница",
            reply_markup=ReplyKeyboardMarkup(
                keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
        )

        return PHONE


async def save_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    phone_number = update.message.contact.phone_number
    user_id = update.effective_user.id

    await context.bot.send_message(
        chat_id=user_id,
        text="Спасибо\n\nПока ожидаете можете подписаться на мой телеграмм канал\n@romanenko_uchit",
        reply_markup=ReplyKeyboardRemove(),
    )

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
                    UPDATE users
                    SET status = ?, phone = ?
                    WHERE id_tg = ?
                """,
            (CONV_HELPER, phone_number, user_id),
        )

        await db.commit()

    """ send to the group """
    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=update.effective_user.name,
    )

    """ kill group job  """
    remove_job_if_exists(name=f"{user_id}-{GROUP_MSG}", context=context)

    """TODO next step"""


async def admin_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    user_id = update.effective_chat.id

    await context.bot.delete_message(
        chat_id=user_id,
        message_id=update.effective_message.message_id,
    )

    if int(query.data) == LEADER_BOARD:
        """send all users"""
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT id, id_tg, status, name, phone FROM users"
            ) as cursor:
                rows = await cursor.fetchall()
                messages = "\n".join(
                    [
                        f"{row[0]}: {row[1]} - {row[2]} - {row[3]} - {row[4]}"
                        for row in rows
                    ]
                )

        if len(messages) != 0:
            await context.bot.send_message(
                chat_id=user_id,
                text="id: tg_id - status - name - phone",
            )

            await context.bot.send_message(
                chat_id=user_id,
                text=messages,
            )
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text="- no users -",
            )

    return await start(update, context)
