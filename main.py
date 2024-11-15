import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config_data.config import Config, load_config
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from handlers import (registration_handler, handler_add_del_learner, handler_add_dz, handler_send_dz,
                      handler_check_dz, learner_handler, other_handlers)
from handlers.registration_handler import storage
from database.models import async_main
from handlers.handler_send_dz import process_scheduler

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import ErrorEvent
import traceback
from aiogram.types import FSInputFile

logger = logging.getLogger(__name__)

async def main():
    await async_main()

    logging.basicConfig(
        level=logging.INFO,
        filename="py_log.log",
        filemode='w',
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')




    logger.info('Starting bot')


    config: Config = load_config()

    bot = Bot(
        token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(process_scheduler, 'cron', day='*', hour=10, args=(bot,))
    scheduler.start()


    dp.include_router(registration_handler.router)
    dp.include_router(handler_add_del_learner.router)
    dp.include_router(handler_add_dz.router)
    dp.include_router(handler_send_dz.router)
    dp.include_router(handler_check_dz.router)
    dp.include_router(learner_handler.router)
    dp.include_router(other_handlers.router)

    @dp.error()
    async def error_handler(event: ErrorEvent):
        logger.critical("Критическая ошибка: %s", event.exception, exc_info=True)
        await bot.send_message(chat_id=config.tg_bot.support_id,
                               text=f'{event.exception}')
        formatted_lines = traceback.format_exc()
        text_file = open('error.txt', 'w')
        text_file.write(str(formatted_lines))
        text_file.close()
        await bot.send_document(chat_id=config.tg_bot.support_id,
                                document=FSInputFile('error.txt'))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())