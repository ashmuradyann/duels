# test_db_connection.py
import aiomysql
import asyncio
from loguru import logger


async def check_uuid(uuid4_str, telegram_id, db_host, db_port, db_user, db_password, db_name):
    conn = await aiomysql.connect(
        host=db_host, port=db_port,
        user=db_user, password=db_password,
        db=db_name
    )
    async with conn.cursor() as cur:
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


async def main():
    # Sample data to test
    uuid4_str = '6b68e8773bbf41d9b8a1de55cb384d4a'
    telegram_id = 'vbxx3'

    # Database credentials

    db_host = 'mysql'
    db_port = 3306
    db_user = 'arcane'
    db_password = 'qsG7zXhh2841'
    db_name = 'so2'

    logger.add("log/test_db_connection.log", rotation="10 MB", level="DEBUG")

    valid_uuid = await check_uuid(uuid4_str, telegram_id, db_host, db_port, db_user, db_password, db_name)
    if valid_uuid:
        logger.info("UUID is valid.")
    else:
        logger.info("UUID is not valid or already linked to a different Telegram user.")


if __name__ == '__main__':
    asyncio.run(main())
