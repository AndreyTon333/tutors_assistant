from config_data.config import load_config, Config
from aiogram.types import Message
import logging

config: Config = load_config()

async def check_super_admin(tg_id: int) -> bool:
    """Проверка на администратора"""
    logging.info('check_super_admin')
    list_super_admin = config.tg_bot.admin_ids.split(',')
    logging.info(f'check_super_admin --- list_super_admin = {list_super_admin}')
    return str(tg_id) in list_super_admin