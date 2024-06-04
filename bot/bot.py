# bot.py
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import aiomysql
import uuid
from loguru import logger


class AsyncTelegramBot:
    def __init__(self):
        self.token = os.environ.get('BOT_TOKEN', "7268716898:AAHfiCKFYv2c1jAOfbAzjwZM4aWXMuW7OE8")
        self.debug = os.environ.get('DEBUG', False)
        self.db_host = os.environ.get('MYSQL_HOST', 'localhost')
        self.db_port = int(os.environ.get('MYSQL_PORT', 3306))
        self.db_user = os.environ.get('MYSQL_USER', 'user')
        self.db_password = os.environ.get('MYSQL_PASSWORD', 'password')
        self.db_name = os.environ.get('MYSQL_DATABASE', 'dbname')

        logger.add("log/bot.log", rotation="10 MB", level="DEBUG" if self.debug else "ERROR")

        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()

    def setup_handlers(self):
        start_handler = CommandHandler('start', self.start)
        button_handler = CallbackQueryHandler(self.handle_button_click)
        self.application.add_handler(start_handler)
        self.application.add_handler(button_handler)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        args = update.message.text.split()
        if len(args) < 2:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid link.")
            return

        uuid4_str = args[1]

        logger.info(f"Received /start from {user_id} with UUID {uuid4_str}")

        valid_uuid = await self.check_uuid(uuid4_str, user_id)

        if not valid_uuid:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="This UUID is not valid or already linked to a different Telegram user.")
            return

        keyboard = [
            [InlineKeyboardButton("Authenticate", callback_data=uuid4_str)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Click to authenticate:",
                                       reply_markup=reply_markup)

    async def check_uuid(self, uuid4_str, telegram_id):
        conn = await aiomysql.connect(
            host=self.db_host, port=self.db_port,
            user=self.db_user, password=self.db_password,
            db=self.db_name
        )
        async with conn.cursor() as cur:
            # Check if a user with the given Telegram ID exists
            await cur.execute('''
                SELECT uuid FROM users_customuser WHERE telegram_id = %s
            ''', (telegram_id,))
            existing_user_result = await cur.fetchone()

            if existing_user_result:
                existing_user_uuid = existing_user_result[0]
                if existing_user_uuid != uuid4_str:
                    # Telegram user exists but with a different UUID
                    return False

            # Check if the UUID exists and is valid
            await cur.execute('''
                SELECT telegram_id, is_authenticated FROM users_customuser WHERE uuid = %s
            ''', (uuid4_str,))
            result = await cur.fetchone()
            logger.info(f"RESULT: {result}")

            if result:
                logger.info(f"Result: {result}")
                stored_telegram_id, is_authenticated = result
                if stored_telegram_id and stored_telegram_id != telegram_id:
                    # UUID exists but is linked to a different Telegram user
                    return False
                if is_authenticated:
                    # UUID exists and is authenticated with the same Telegram ID
                    return True
                # UUID exists and is not authenticated
                return True
            return False

    async def handle_button_click(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        uuid4_str = query.data
        telegram_id = query.from_user.id
        logger.info(f"Button clicked by user with UUID: {uuid4_str} and Telegram ID: {telegram_id}")

        if await self.confirm_uuid(uuid4_str, telegram_id):
            await query.edit_message_text(text="UUID confirmed. You can now authenticate.")
        else:
            await query.edit_message_text(text="UUID confirmation failed.")

    async def confirm_uuid(self, uuid4_str, telegram_id):
        conn = await aiomysql.connect(
            host=self.db_host, port=self.db_port,
            user=self.db_user, password=self.db_password,
            db=self.db_name
        )
        async with conn.cursor() as cur:
            await cur.execute('''
                SELECT 1 FROM users_customuser WHERE uuid = %s AND (telegram_id IS NULL OR telegram_id = %s)
            ''', (uuid4_str, telegram_id))
            result = await cur.fetchone()
            if result:
                await cur.execute('''
                    UPDATE users_customuser
                    SET telegram_id = %s, is_authenticated = TRUE
                    WHERE uuid = %s
                ''', (telegram_id, uuid4_str))
                await conn.commit()
        conn.close()
        return result is not None

    def run(self):
        logger.info("Starting bot")
        self.application.run_polling()


if __name__ == '__main__':
    bot = AsyncTelegramBot()
    bot.run()
