from aiogram import F, Router, Bot
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, default_state, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from secrets import token_urlsafe

from handlers.handler_add_dz import process_hello_admin

import keyboards.keyboards as kb
import database.requests as rq


router = Router()


import logging
import asyncio




@router.message(F.text == 'Ученики')
async def process_learner(message:Message, bot: Bot, state: FSMContext):
    """Срабатывает на reply кнопку 'Ученики'"""
    logging.info('process_learner')

    if 'hello_message' not in (await state.get_data()):
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
        except:
            pass
    else:
        await state.clear()
    #await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
   # await bot.send_message(
   #     chat_id=message.chat.id,
   #     text='Приветствую Вас!\nВы являетесь администратором проекта!',
   #     reply_markup=kb.kb_admin_dz_lrn())
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except:
        pass
    await message.answer(text='Добавить или удалить ученика',
                         reply_markup=await kb.kb_add_and_del_learner())


@router.callback_query(F.data == 'add_token')
async def process_add_token(clb: CallbackQuery, bot: Bot) -> None:
    """Генерация токена, занесение его в БД"""
    logging.info('process_add_token')
    #await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id)

    token_new = str(token_urlsafe(8))
    dict_={'token': token_new}
    await rq.add_token(dict_)

    await clb.message.answer(
        text=f"Отправте ученику токен <code>{token_new}</code> для верификации в боте"
    )
    await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id)
    await clb.answer()



@router.callback_query(F.data == 'del_learner')
async def process_del_learner(clb: CallbackQuery, bot: Bot) -> None:
    """Список учеников для удаления"""
    logging.info('process_del_learner')

    list_learners = [learner for learner in await rq.get_all_learners()]
    logging.info(f"list_learners = {list_learners}")
    if not list_learners:
        await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id)
        await clb.answer(text='Нет учеников для удаления', show_alert=True)
        return
    #  kb.kb_choise_learners ---  button = f'{action}!{id_dz}!{learner.id}' # action = delete_learner || action = send_dz
    keyboard = kb.kb_choise_learners(
        action='delete_learner',
        list_learners=list_learners,
        back=0,
        forward=2,
        count=6,
        id_dz=10000000)
    await clb.message.edit_text(
        text='Выберите ученика для удаления его из бота',
        reply_markup=keyboard
    )
    await clb.answer()


# >>>>
@router.callback_query(F.data.startswith('delete_learnerforward'))
async def process_forward(clb: CallbackQuery) -> None:
    logging.info(f'process_forward: {clb.message.chat.id} ----- clb.data = {clb.data}')
    list_learners = [learner for learner in await rq.get_all_learners()]
    forward = int(clb.data.split('!')[-1]) + 1
    back = forward - 2
    keyboard = kb.kb_choise_learners(action='delete_learner', list_learners=list_learners, back=back, forward=forward, count=6)
    try:
        await clb.message.edit_text(text='Выберитe ученика, кoторого нужно удалить',
                                         reply_markup=keyboard)
    except:
        await clb.message.edit_text(text='Выберитe ученика, которого нужно удалить',
                                         reply_markup=keyboard)
    await clb.answer()


# <<<<
@router.callback_query(F.data.startswith('delete_learnerback'))
async def process_back(clb: CallbackQuery) -> None:
    logging.info(f'process_back: {clb.message.chat.id} ----- clb.data = {clb.data}')
    list_learners = [learner for learner in await rq.get_all_learners()]

    back = int(clb.data.split('!')[-1]) - 1
    forward = back + 2
    keyboard = kb.kb_choise_learners(action='delete_learner', list_learners=list_learners, back=back, forward=forward, count=6)
    try:
        await clb.message.edit_text(text='Выберитe ученика, кoторого нужно удалить',
                                         reply_markup=keyboard)
    except:
        await clb.message.edit_text(text='Выберитe ученика, которого нужно удалить',
                                         reply_markup=keyboard)
    await clb.answer()


    # подтверждение удаления ученика из базы
@router.callback_query(F.data.startswith('delete_learner'))
async def process_delete_learner(clb: CallbackQuery) -> None:
    logging.info(f'process_delete_learner: {clb.message.chat.id} clb.data = {clb.data}')

     #  kb.kb_choise_learners ---  button = f'{action}!{id_dz}!{learner.id}' # action = delete_learner || action = send_dz
    id_learner = clb.data.split('!')[-1]
    data_learner = await rq.get_learner_id(id=id_learner)
    fio = data_learner.fio

    postfix = f"{fio}!{id_learner}"
    await clb.message.edit_text(
        text=f'Удалить ученика {fio}',
        reply_markup=kb.kb_delete_learner_after_confirm(postfix=postfix)
    )
    await clb.answer()


# отмена удаления пользователя
@router.callback_query(F.data.startswith('notdel_learner'))
async def process_notdel_learner(clb: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    logging.info(f'process_notdel_learner: {clb.message.chat.id} clb.data = {clb.data}')
    await process_hello_admin(message=clb.message, state=state, bot=bot)
    #await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id)
    await clb.answer(
        text='Удаление ученика отменено',
        show_alert=True
    )


# удаление после подтверждения
@router.callback_query(F.data.startswith('del_learner_confirm'))
async def process_descriptiondel_learner(clb: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    logging.info(f'process_descriptiondel_learner: {clb.message.chat.id} clb.data = {clb.data}')
    fio = clb.data.split('!')[-2]
    id = clb.data.split('!')[-1]

    await rq.delete_learner(id=int(id))
    #await clb.message.answer(text=f'Ученик {fio} успешно удален')
    await asyncio.sleep(3)

    #await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id)
    await clb.answer(
        text=f'Ученик {fio} успешно удален',
        show_alert=True
    )
    await bot.delete_message(
        chat_id=clb.message.chat.id,
        message_id=clb.message.message_id
    )
    #await process_hello_admin(message=clb.message, state=state, bot=bot)