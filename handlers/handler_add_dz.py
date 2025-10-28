from datetime import date, datetime
from aiogram import F, Router, Bot

from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, default_state, StatesGroup
from aiogram.fsm.context import FSMContext
#from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
#from filter.user_filter import IsChatPrivate



import keyboards.keyboards as kb
import database.requests as rq


router = Router()
#router.message.filter(IsChatPrivate())

#storage = MemoryStorage()

import logging
import asyncio
import random

class AddDZ(StatesGroup):
    state_add_name_dz = State()
    state_add_content = State()


async def process_hello_admin(message: Message, state: FSMContext, bot: Bot):
    """Показываю сообщение: 'Приветствую Вас! Вы являетесь администратором проекта!' и вывожу reply кнопки 'ДЗ' 'Ученики'"""
    logging.info('process_hello_admin')
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        logging.info('Удаление сообщения СТРОКА 37')
    except:
        pass

    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
        logging.info('Удаление сообщения СТРОКА 43')
    except:
        pass
    await state.set_state(state=None)

    #await bot.send_message(
    #    chat_id=message.chat.id,
    #    text='Приветствую Вас!\nВы являетесь администратором проекта!',
    #    reply_markup=kb.kb_admin_dz_lrn())


@router.message(F.text == 'Домашнее задание')
async def process_home_task(message:Message, bot:Bot, state: FSMContext):
    """Срабатывает на reply кнопку 'Домашнее задание'"""
    logging.info('process_home_task')

    #if 'Приветствую вас' not in """как обратиться к тексту -1 сообщения?""":
    #    # чтобы удалялась именно инлайн клавиатура, а реплай оставалась
    #    try: #чтобы не висела инлайн клавиатура
    #        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
    #    except:
    #        pass

    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except:
        pass

    if 'hello_message' not in (await state.get_data()):
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
        except:
            pass
    else:
        await state.clear()

    #await bot.send_message(
    #    chat_id=message.chat.id,
    #    text='Приветствую Вас!\nВы являетесь администратором проекта!',
    #    reply_markup=kb.kb_admin_dz_lrn())
    await message.answer(
        text='Вы можете добавить ДЗ и проверить задания, присланные учениками на проверку.',
        reply_markup=await kb.kb_send_add_check_dz())
    #await message.answer(text='Вы можете добавить ДЗ и проверить задания, присланные учениками на проверку.',
     #                    reply_markup=await kb.kb_send_add_check_dz())



@router.callback_query(F.data == 'add_dz')
async def process_add_dz(clb: CallbackQuery, bot: Bot):
    """Срабатывает на inline кнопку 'Добавить ДЗ' в разделе 'Домашнее задание'"""
    logging.info('process_add_dz')
    try:
        await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id)
    except:
        pass

    await clb.message.answer(
        text='Выберите раздел домашнего задания из списка',
        reply_markup=kb.kb_name_chapter_dz(prefix='process_add_dz'))
    await clb.answer()


@router.callback_query(F.data.startswith('process_add_dz'))
async def process_add_dz_send_name_dz(clb: CallbackQuery, bot: Bot, state: FSMContext):
    """Перевод в режим ожидания ввода названия для ДЗ"""
    logging.info('process_add_dz_send_name_dz')
    await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id)

    await state.update_data(chapter=clb.data.split('!')[-1]) # запоминаем название раздела (ЕГЭ, ОГЭ, классы)
    await state.set_state(state=AddDZ.state_add_name_dz)

    await clb.message.answer(text=
                                f"Пришлите название для задания.\n\n"
                                f"Справка - название должно быть осмысленное и короткое, так как оно будет выводится в списке "
                                f"кнопок для выбора заданий для отправки ученикам")
    await clb.answer()


@router.message(AddDZ.state_add_name_dz)
async def process_add_dz_send_content(message: Message, bot: Bot, state: FSMContext):
    """Перевод в режим ожидания получения контента с ДЗ"""
    logging.info('process_add_dz_send_content')

    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id-1)

    await state.update_data(name_dz=message.text)
    await state.set_state(state=AddDZ.state_add_content)
    data_=await state.get_data()
    #logging.info(f"data = {data_}")
    await message.answer(
        text=f"Пришлите контент для задания 📎. \nКонтент может быть текстом с сылками, фотографиями или файлом.\n\n"
        f"Если вы хотите прислать текстовый комментарий к домашнему заданию, пришлите его первым отдельным сообщением,"
        f" не прикрепляя к фотографии или файлу.")


@router.message(AddDZ.state_add_content)
async def process_add_dz_save_content_add_content(message: Message, bot: Bot, state: FSMContext):
    """Получение и сохранение контента, предложение отправить еще"""
    logging.info('process_add_dz_save_content_add_content')


    await asyncio.sleep(random.random())

    data = await state.get_data()
    list_content = data.get('content', [])# метод get у словаря: если есть ключ 'content', то выдаст его, если нет, то пустой список
    count = data.get('count', [])
    #logging.info(f"STROKA 105 --- list_content = {list_content}")

    if message.text:
        # получаем что есть в state data.text
        data_text = await state.get_data()
        if 'text' not in data_text:
            await state.update_data(text=message.text)
        else:
            data_text_new = data_text['text'] + ',!?!,' + message.text
            await state.update_data(text=data_text_new)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await message.answer(text='Пришлите контент для задания 📎',
                             reply_markup=kb.kb_save_add_dz(endfix = 'add_dz'))

        return

    elif message.photo:
        content = message.photo[-1].file_id

    elif message.document:
        content = message.document.file_id

    list_content.append(content)
    count.append(content)

    await state.update_data(content=list_content)
    await state.update_data(count=count)
    await state.set_state(state=None)

    if len(count) == 1:
        await message.answer(
        text='Вы можете добавить контент к домашнему заданию, для этого нажмите "Добавить ещё", а можете загрзить его в базу данных.',
        reply_markup=kb.kb_save_add_dz(endfix = 'add_dz'))
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except:
        pass
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
    except:
        pass

@router.callback_query(F.data.endswith('add_dz'))
async def process_add_dz_written_content_to_bd(clb: CallbackQuery, state: FSMContext, bot: Bot):
    logging.info(f'process_add_dz_written_content_to_bd {clb.message.chat.id}')

    #await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id-1)
    #await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id)
    answer = clb.data.split('!')[0]

    if answer == 'add_more':
        await state.set_state(AddDZ.state_add_content)
        await state.update_data(count=[])
        await clb.message.answer(
            text='Пришлите контент для задания 📎')


    elif answer == 'continue':
        ### Сделать вариант обработки, если контент прислан не был. Только текст
        #logging.info(f"await state.get_data() = {await state.get_data()}")

        if 'content' in (await state.get_data()):
            data_list_content = (await state.get_data())['content']
            str_content = ','.join(data_list_content)
            await state.update_data(content = str_content)
            #logging.info(f"await state.get_data() = {await state.get_data()}")
        dict_content = await state.get_data()
        if 'count' in dict_content:
            del dict_content['count']

        await rq.add_content(dict_content)
        logging.info(f"--- await state.get_data() = {await state.get_data()} ---- dict_content = {dict_content}")


        #await asyncio.sleep(3)
        # await clb.answer(
        #     text=f'Вы добавили домашнее задание "{dict_content["name_dz"]}". Вы можете продолжать добавлять ДЗ.',
        #     show_alert=True
        # )

        await bot.send_message(
            chat_id=clb.message.chat.id,
            text=f'Вы добавили домашнее задание "{dict_content["name_dz"]}". Вы можете продолжать добавлять ДЗ.',
            reply_markup=kb.kb_name_chapter_dz())

        await state.clear()
        await state.set_state(state=None)
        await process_add_dz(clb=clb, bot=bot)

    #await clb.answer()
