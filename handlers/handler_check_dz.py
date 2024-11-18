from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, default_state, StatesGroup
from aiogram.fsm.context import FSMContext
from datetime import datetime, date, timedelta

from aiogram.types import ReplyKeyboardRemove

from handlers.handler_add_dz import process_hello_admin
from handlers.handler_send_dz import dict_chapter
import keyboards.keyboards as kb
import database.requests as rq


router = Router()

import logging
import asyncio
import random

class CheckDzFSM(StatesGroup):
    state_send_dz = State()


@router.callback_query(F.data == 'check_dz')
async def process_check_dz_step1(clb: CallbackQuery, bot: Bot):
    """Если ДЗ на проверку нет, то Alert = 'нет дз'. Если 'да', то кнопки 'Все верно' и 'Исправить' """
    logging.info('proess_check_dz_step1')
    tg_id = clb.message.chat.id

    count_check_dz = await rq.get_count_executed_dz()
    if count_check_dz == 0:
        await clb.answer(
            text='Домашнего задания для проверки нет',
            show_alert=True
        )
        return
    else:
        try:
            await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id)
        except:
            pass
        data_executed_dz = await rq.get_dz_to_executed() # этот метод возвращает список строк таблицы Relation
        logging.info(f"data_executed_dz = {data_executed_dz}")

        one_executed_dz = data_executed_dz[0] # это одна строка из таблицы Relation
        if one_executed_dz.comment_to_execute_dz: # если есть comment_to_execute_dz в таблице Relation
            logging.info(f"one_executed_dz.comment_to_execute_dz = {one_executed_dz.comment_to_execute_dz}")
            comment_to_execute_dz = one_executed_dz.comment_to_execute_dz
            list_comment_to_execute_dz = comment_to_execute_dz.split(',!?!,')
            for item in list_comment_to_execute_dz:
                if 'https://' not in item: # сперва выводим комменты к ДЗ
                    await bot.send_message(chat_id=tg_id, text=item)
            for item in list_comment_to_execute_dz:
                if 'https://' in item: # затем выводим тексты ссылок
                    await bot.send_message(chat_id=tg_id, text=item)

        if one_executed_dz.executed_dz: # Если есть строка (контент) в колонке executed_dz
            logging.info(f"one_executed_dz.executed_dz = {one_executed_dz.executed_dz}")
            execeted_dz = one_executed_dz.executed_dz
            list_executed_dz = execeted_dz.split(',')
            for item in list_executed_dz:
                try:
                    await bot.send_photo(chat_id=tg_id, photo=item)
                except:
                    try:
                        await bot.send_document(chat_id=tg_id, document=item)
                    except:
                        try:
                            await bot.send_message(chat_id=tg_id)
                        except:
                            pass
        keyboard = kb.kb_all_right_check_dz(id_relation=one_executed_dz.id)
        await clb.message.answer(
            text=f'Ученик {one_executed_dz.fio} отправил домашнее задание на проверку',
            reply_markup=keyboard
        )
    await clb.answer()
        # после отправки ДЗ



@router.callback_query(F.data.startswith('all_right_dz'))
async def process_check_dz_all_right_dz(clb: CallbackQuery, bot: Bot):
    """Если нажато 'Все верно' """
    logging.info('proess_check_dz_all_right_dz')
    tg_id = clb.message.chat.id

    id_relation = clb.data.split('!')[-1]
    # установка значения "Все верно" в колонку checked_dz
    await rq.set_attribute_relation(id_relation=id_relation,
                                    attribute = 'checked_dz',
                                    set_attribute = 'Всё верно'
                                    )

    await process_check_dz_step1(clb=clb, bot=bot)
    await clb.answer()



@router.callback_query(F.data.startswith('fix_dz'))
async def process_check_dz_fix_dz(clb: CallbackQuery, state: FSMContext):
    """Если нажато 'Исправить', установка состояния ожидания ввода текса и контента """
    logging.info('proess_check_dz_fix_dz')
    #tg_id = clb.message.chat.id

    id_relation = clb.data.split('!')[-1]

    await state.set_state(CheckDzFSM.state_send_dz)
    await state.update_data(id_relation = id_relation)
    await clb.message.answer(
        text=f'Пришлите контент проверенного домашнего задания для отправки ученику. '
        f'Контент может быть текстом с ссылками, фотографиями или файлами'
        )
    await clb.answer()



@router.message(CheckDzFSM.state_send_dz)
async def process_check_dz_fix_dz_send_dz(message: Message, state: State):
    """Ввод текста и контекста"""
    logging.info('process_check_dz_fix_dz_send_dz')

    await asyncio.sleep(random.random())

    data = await state.get_data()
    list_checked_dz = data.get('checked_dz', [])  # метод get у словаря: если есть ключ 'checked_dz', то выдаст его, если нет, то пустой список
    count = data.get('count', [])
    logging.info(f"НАЧАЛО await state.get_data() = {await state.get_data()}")
    if message.text:
        # получаем что есть в state data.text
        data_text = await state.get_data()
        if 'comment_checked_dz' not in data_text:
            await state.update_data(comment_checked_dz=message.text)
        else:
            data_text_new = data_text['comment_checked_dz'] + ',!?!,' + message.text
            await state.update_data(comment_checked_dz=data_text_new)

        await message.answer(
            text='Пришлите контент для задания 📎',
            reply_markup=kb.kb_check_dz_add_more_check_next())
        return


    elif message.photo:
        checked_dz = message.photo[-1].file_id

    elif message.document:
        checked_dz = message.document.file_id


    list_checked_dz.append(checked_dz)
    count.append(checked_dz)

    logging.info(f"checked_dz = {checked_dz} --- list_checked_dz = {list_checked_dz} --- count = {count}")

    await state.update_data(checked_dz=list_checked_dz)
    await state.update_data(count=count)
    await state.set_state(state=None)

    logging.info(f"КОНЕЦ await state.get_data() = {await state.get_data()}")

    if len(count) == 1:
        await message.answer(
        text=f'Вы можете добавить контент к проверенному домашнему заданию, для этого нажмите "Добавить ещё", '
        f'а можете загрзить его в базу данных и перейти к проверке следующего ДЗ, для этого нажмите "Проверить следующее ДЗ".',
        reply_markup=kb.kb_check_dz_add_more_check_next())


@router.callback_query(F.data == 'add_more_check_dz')
@router.callback_query(F.data == 'check_next_dz')
async def process_check_dz_last_step(clb: CallbackQuery, state: State, bot:Bot) -> None:
    """Или 'Добавить ещё' ДЗ или переход к проверке нового ДЗ. тогда занести в БД проверенное ДЗ"""
    logging.info('process_check_dz_last_step')

    if clb.data == 'add_more_check_dz':
        await state.set_state(CheckDzFSM.state_send_dz)
        await state.update_data(count=[])
        await clb.message.edit_text(
            text='Пришлите контент для задания 📎')

    elif clb.data == 'check_next_dz':
        data_checked_dz = await state.get_data()
        logging.info(data_checked_dz)

        str_checked_dz: str = ''
        if 'comment_checked_dz' in data_checked_dz or 'checked_dz' in data_checked_dz:
            if 'checked_dz' in data_checked_dz:
                data_list_checked_dz = (await state.get_data())['checked_dz']
                str_checked_dz = ','.join(data_list_checked_dz)
                await rq.set_attribute_relation(
                    id_relation=data_checked_dz['id_relation'],
                    attribute='checked_dz',
                    set_attribute=str_checked_dz)

            if 'comment_checked_dz' in data_checked_dz:
                str_checked_dz = (await state.get_data())['comment_checked_dz']
                await rq.set_attribute_relation(
                    id_relation=data_checked_dz['id_relation'],
                    attribute='comment_checked_dz',
                    set_attribute=str_checked_dz)


            # отправка ученику сообщения
            data_dz = await rq.get_data_relation_from_id(id=data_checked_dz['id_relation'])
            await bot.send_message(
                chat_id=data_dz.tg_id,
                text=f'Вы получили правки по домашнему заданию {data_dz.name_dz}, срок выполнения - {data_dz.deadline}'
            )

            # переход к функции process_check_dz_step1
            await process_check_dz_step1(clb=clb, bot=bot)
            await state.clear()

        else:
            await clb.message.answer(
                text='Добавте контент к домашнему заданию'
            )
            await process_check_dz_fix_dz_send_dz(message=clb.message, state=state)
    await clb.answer()


# await state.update_data(comment_checked_dz
# await state.update_data(checked_dz
# await state.update_data(id_relation