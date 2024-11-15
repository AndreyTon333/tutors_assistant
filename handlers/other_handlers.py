from aiogram import Router
from aiogram.types import Message
router = Router()
import logging


# Хэндлер для сообщений, которые не попали в другие хэндлеры
@router.message()
async def send_answer_other(message: Message):
    logging.info('send_answer_other')
    await message.answer(text=f'❌ <b>Неизвестная команда!</b>\n'
                              f'Обновите Меню, нажав /start')#,
                               #parse_mode='html')
