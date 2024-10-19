#!/usr/bin/env python
# pylint: disable=unused-argument

import os
import logging
import re
from typing import Optional, Tuple

import telegram
from datetime import timedelta

from telegram import Update, Chat, ChatMember, ChatMemberUpdated
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, ChatMemberHandler, filters

from anti_flood import is_flood
from blacklist_manager import BlacklistManager
from db.dao.DAO import DAO
from db.dao.NoOpDao import NoOpDao
from db.dao.AbstractDAO import AbstractDAO
import db.connection_manager

tg_bot_token = os.environ['TG_BOT_TOKEN']
forward_group_id = int(os.environ['TG_FORWARD_GROUP_ID'])
start_message = os.environ['START_MESSAGE']

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

blacklist_manager = BlacklistManager()

dao: AbstractDAO = DAO() if os.environ.get("DB_CONNECTION_STRING") else NoOpDao()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # start_message_file = open(start_message_file_location, "r", encoding="utf8")
    # start_message = start_message_file.read()
    await update.message.reply_text(start_message, parse_mode=telegram.constants.ParseMode.HTML)


async def handle_msg_from_user_to_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id == forward_group_id:
        await handle_reply_in_group(update, context)
    else:
        await handle_msg_from_client(update, context)


async def _send_msg(update: Update, msg: str, chat_id: int | str):
    if update.message.photo:
        await update.get_bot().send_photo(chat_id=chat_id, caption=msg, photo=update.message.photo[0])
    elif update.message.video:
        await update.get_bot().send_video(chat_id=chat_id, caption=msg, video=update.message.video)
    elif update.message.document:
        await update.get_bot().send_document(chat_id=chat_id, caption=msg, document=update.message.document)
    elif update.message.audio:
        await update.get_bot().send_audio(chat_id=chat_id, caption=msg, document=update.message.audio)
    else:
        await update.get_bot().sendMessage(chat_id=chat_id, text=msg)

def _save_msg(update: Update, client_msg_text):
    text = client_msg_text
    binary_id = ""

    user_id = str(update.effective_user.id)
    username = update.effective_user.username
    full_name = update.effective_user.full_name

    if update.message.photo:
        binary_id = f"Photo={update.message.photo[0].file_unique_id}"
    elif update.message.video:
        binary_id = f"Video={update.message.video.file_unique_id}"
    elif update.message.document:
        binary_id = f"Document={update.message.document.file_unique_id}"
    elif update.message.audio:
        binary_id = f"Document={update.message.audio.file_unique_id}"
    else:
        pass

    user = dao.get_user_by_id(user_id)
    if not user:
        dao.insert_user(user_id, username, full_name)

    dao.insert_message(user_id, update.message.date + timedelta(hours=3), text, binary_id)


async def handle_msg_from_client(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username
    full_name = update.effective_user.full_name

    if blacklist_manager.is_blacklisted(user_id):
        logger.info(f"User #{user_id} attempted to send a message, but he is BLOCKED")
        return

    if is_flood(user_id):
        logger.info(f"Flood detected, userId={user_id} ({username})")
    else:
        client_msg_text = update.message.text or update.message.caption or ""
        client_msg_text = re.sub(r'(https?:\/\/)(\s)*(www\.)?(\s)*((\w|\s)+\.)*([\w\-\s]+\/)*([\w\-]+)((\?)?[\w\s]*=\s*[\w\%&]*)*', '!ССЫЛКА УДАЛЕНА!', client_msg_text, flags=re.MULTILINE)

        msg = f"Новое сообщение от #id{user_id} (@{username}) ({full_name})\n{client_msg_text}"

        await _send_msg(update, msg, forward_group_id)
        _save_msg(update, client_msg_text)


async def handle_reply_in_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_to_msg = update.effective_message.reply_to_message

    if reply_to_msg:
        msg = update.effective_message.text or update.effective_message.caption or ""
        msg_sender_id = re.search("^Новое сообщение от #id(.*) ", reply_to_msg.text or reply_to_msg.caption).group(1)

        await _send_msg(update, msg, msg_sender_id)


def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


async def track_blocked(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = extract_status_change(update.my_chat_member)
    if result is None:
        return
    was_member, is_member = result

    user_id = update.effective_user.id
    username = update.effective_user.username
    full_name = update.effective_user.full_name

    # Handle chat types differently:
    chat = update.effective_chat
    if chat.type == Chat.PRIVATE:
        msg: str = ""
        if not was_member and is_member:
            msg = f"РАЗБЛОКИРОВКА бота пользователем #id{user_id} (@{username}) ({full_name})"
        elif was_member and not is_member:
            msg = f"БЛОКИРОВКА бота пользователем #id{user_id} (@{username}) ({full_name})"
        logger.info(msg)
        await update.get_bot().sendMessage(chat_id=forward_group_id, text=msg)


def main() -> None:
    logger.info(f"forward_group_id='{forward_group_id}'")
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(tg_bot_token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(ChatMemberHandler(track_blocked))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_msg_from_user_to_bot))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
