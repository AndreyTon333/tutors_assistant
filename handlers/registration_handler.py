from aiogram import F, Router, Bot

from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, default_state, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove

from handlers.handler_add_dz import process_hello_admin
from filter.filter import check_super_admin

import keyboards.keyboards as kb
import database.requests as rq


router = Router()

storage = MemoryStorage()

import logging

class Registration(StatesGroup):
    state_token = State()
    state_fio = State()

@router.message(CommandStart())
async def process_start_command(message: Message,  state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_start_command')
    await state.set_state(state=None)
    tg_id = message.chat.id

    #делаем проверку на администратора, если ДА, запускаем функцию 'hello_admin'
    if await check_super_admin(tg_id=tg_id):
        await bot.send_message(
            chat_id=message.chat.id,
            text='Приветствую Вас!\nВы являетесь администратором проекта!',
            reply_markup=kb.kb_admin_dz_lrn())
        await state.update_data(hello_message='Приветствую')
        return

    # Пользователь верифицирован? Он есть в БД
    if await rq.is_learner_in_database(tg_id=tg_id):
        await process_begin_without_state(message=message, state=state)
    else:
        await message.answer(
            text='Пришлите мне токен, который вы получили от администратора проекта'
        )
        await state.set_state(state=Registration.state_token)



@router.message(Registration.state_token)
async def process_check_token(message: Message, state: FSMContext, bot:Bot) -> None:
    """Ввод токена, проверка на наличие его в БД, начало регистрации"""
    logging.info('process_check_token')

    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    try:
        await bot.delete_message(chat_id=message.chat.id,message_id=message.message_id-1)
    except:
        pass

    token = message.text # ловим токен от пользователя
    if await rq.is_token_valid(token=token): # есть ли этот токен в БД и не использовали ли его при регистрации?
        await state.update_data(token = token)
        if message.chat.username:
            await state.update_data(username = message.chat.username)
        else:
            await state.update_data(username = 'username')

        await state.update_data(tg_id = message.chat.id)


        keyboard = kb.kb_registration()
        await message.answer(
            text='Вы успешно прошли верификацию в боте. Пройдите регистрацию, чтобы получать ДЗ.',
            reply_markup=keyboard
        )
    else:
        await message.answer(
            text='Токен не прошел проверку, запросите новый токен у Администратора'
        )


@router.callback_query(F.data == 'registration')
async def process_given_fio(clb: CallbackQuery, state: FSMContext):
    """Запрашивает ФИО"""
    logging.info('process_given_fio')

    await state.set_state(state=Registration.state_fio)
    await clb.message.edit_text(
        text='Пришлите ваши Фамилию Имя\n(например, Иванов Иван)',
        reply_markup=None
    )


@router.message(Registration.state_fio)
async def process_begin_state_fio(message: Message, bot: Bot, state: FSMContext) -> None:
    """Стартовая функция ученика при входе, если есть не было регистрации и пришли через state_fio"""
    logging.info("process_begin_state_fio")
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    try:
        await bot.delete_message(chat_id=message.chat.id,message_id=message.message_id-1)
    except:
        pass
    # ещё раз надо проверить валидность токена, вдруг пока регистрировался его заняли
    data_registration = await state.get_data()
    fio = message.text
    token = data_registration['token']
    if await rq.is_token_valid(token=token):
        data_registration['fio']=fio
        await rq.add_learner(data=data_registration)

        keyboard = kb.kb_learner_begin()
        await message.answer(
            text=
            f'Отлично! Вы прошли регистрацию. \nТеперь бот будет присылать вам ДЗ.\n'
            f'После выполнения ДЗ вы можете отправить его на проверку при помощи кнопки ниже "Отправить ДЗ на проверку", '
            f'а также посмотреть ваши ДЗ и комментарии к ним от репетитора.',
            reply_markup=keyboard

    )
        await state.clear()
    else:
        await message.answer(
            text='Токен не прошел проверку, запросите новый токен у Администратора'
        )

        await state.set_state(state=Registration.state_token)




async def process_begin_without_state(message: Message, state: FSMContext):
    """Стартовая функция ученика при входе, если есть регистрация"""
    logging.info("process_begin_without_state")


    keyboard = kb.kb_learner_begin()
    await message.answer(
        text=f'После выполнения ДЗ вы можете отправить его на проверку при помощи кнопки ниже "Отправить ДЗ на проверку", '
        f'а также посмотреть ваши ДЗ и комментарии к ним от репетитора.',
        reply_markup=keyboard
    )
    await state.update_data(first_message='first_message')
