from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

import aiosqlite

from romanenko_uchit_bot.static.ids import ADMINS
from romanenko_uchit_bot.static.conversions import CONV_REGISTERED, CONV_GUIDE
from romanenko_uchit_bot.static.states import PROGREV_MESSAGES, ADMIN_COMMANDS
from romanenko_uchit_bot.static.callbacks import (
    CONVERSIONS,
    LEADER_BOARD,
    MAIL,
    GETTING_GUIDE,
)

from romanenko_uchit_bot.database.db import DB_PATH

from romanenko_uchit_bot.tools.escape_text import escape_text

from romanenko_uchit_bot.jobs.jobs import way_to_it_job, ONCE_WAY_IT_JOB


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id

    if update.effective_user.id in ADMINS:
        """ Open Admin Panel """

        keyboard = [
            [
                InlineKeyboardButton("Conversions", callback_data=CONVERSIONS),
                InlineKeyboardButton("List of Users", callback_data=LEADER_BOARD),
            ],
            [
                InlineKeyboardButton("Send everyone", callback_data=MAIL),
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
        """ Register User """

        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT name FROM users WHERE id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    """ Already Registered """
                    print("Вы уже зарегистрированы")

                else:
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

        with open("romanenko_uchit_bot/img/me.jpeg", "rb") as f:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=f,
                caption=escape_text("Кто я?\n\n*- Владимир Романенко*"),
                parse_mode=ParseMode.MARKDOWN_V2,
            )

        context.job_queue.run_once(
            way_to_it_job, 15, chat_id=user_id, name=f"{user_id}-{ONCE_WAY_IT_JOB}"
        )

        return PROGREV_MESSAGES

        """ SEND TO GROUP """
        # message = update.effective_message.id
        # await context.bot.forwardMessage(
        #     chat_id=GROUP_ID, from_chat_id=update.effective_chat.id, message_id=message
        # )


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
                    WHERE id = ?
                """,
                (CONV_GUIDE, user_id),
            )

            await db.commit()

        await context.bot.send_message(
            chat_id=user_id,
            text=escape_text("*Гайд*"),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
