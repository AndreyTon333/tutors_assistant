from aiogram import Router
from aiogram.types import Message, FSInputFile
router = Router()
import logging


# Хэндлер для сообщений, которые не попали в другие хэндлеры
@router.message()
async def send_answer_other(message: Message):
    logging.info('send_answer_other')
    if message.text == '/get_logfile':
        logging.info(f'all_message message.admin./get_logfile')
        file_path = "py_log.log"
        await message.answer_document(FSInputFile(file_path))
        return

    if message.text == '/get_dbfile':
        logging.info(f'all_message message.admin./get_dbfile')
        file_path = "database/db.sqlite3"
        await message.answer_document(FSInputFile(file_path))
        return

    await message.answer(text=f'❌ <b>Неизвестная команда!</b>\n'
                              f'Обновите Меню, нажав /start')#,
                               #parse_mode='html')
