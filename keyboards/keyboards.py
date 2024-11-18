from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder
import database.requests as rq
import logging



def kb_admin_dz_lrn() -> ReplyKeyboardMarkup:
    """Reply - клавиатура 'Домашнее задание' и 'Ученики' """
    logging.info('kb_admin_dz_lrn')

    button_1 = KeyboardButton(text='Домашнее задание')
    button_2 = KeyboardButton(text='Ученики')

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1],[button_2]],
        resize_keyboard=True
    )
    return keyboard


async def kb_send_add_check_dz() -> InlineKeyboardMarkup:
    """Отправить ДЗ, добавить ДЗ, проверить ДЗ. Проверка в БД сколько ДЗ надо порверить."""
    logging.info('kb_send_add_check_dz')

    # В БД узнаем сколько ДЗ надо проверить
    count_check_dz=await rq.get_count_executed_dz()
    button_send=InlineKeyboardButton(
        text='Отправить ДЗ',
        callback_data='send_dz'
    )
    button_add=InlineKeyboardButton(
        text='Добавить ДЗ',
        callback_data='add_dz'
    )
    button_check=InlineKeyboardButton(
        text=f"Проверить ДЗ ({count_check_dz})",
        callback_data='check_dz'
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [button_send], [button_add], [button_check]
        ]
    )
    return keyboard


def kb_name_chapter_dz(prefix: str) -> InlineKeyboardMarkup:
    """Инлайн клавиатура 'ЕГЭ' 'ЕГЭ(варианты)' 'ОГЭ' '10 класс' '9 класс' '8 класс' """
    logging.info("kb_name_chapter_dz")

    button_EGE=InlineKeyboardButton(
        text='ЕГЭ',
        callback_data=f"{prefix}!EGE"
    )
    button_EGE_variants=InlineKeyboardButton(
        text='ЕГЭ (варианты)',
        callback_data=f"{prefix}!EGE_variants"
    )
    button_OGE=InlineKeyboardButton(
        text='ОГЭ',
        callback_data=f"{prefix}!OGE"
    )
    button_10class=InlineKeyboardButton(
        text='10 класс',
        callback_data=f"{prefix}!10class"
    )
    button_9class=InlineKeyboardButton(
        text='9 класс',
        callback_data=f"{prefix}!9class"
    )
    button_8class=InlineKeyboardButton(
        text='8 класс',
        callback_data=f"{prefix}!8class"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [button_EGE], [button_EGE_variants], [button_OGE], [button_10class], [button_9class], [button_8class]
        ]
    )
    return keyboard

def kb_save_add_dz(endfix: str) -> InlineKeyboardMarkup:
    """инлайн кнопки 'Добавить ещё' и 'Отправить'"""
    logging.info('kb_save_add_dz')

    button_add=InlineKeyboardButton(
        text='Добавить ещё',
        callback_data=f'add_more!{endfix}'
    )
    button_continue=InlineKeyboardButton(
        text='Отправить',
        callback_data=f'continue!{endfix}'
    )

    keyboard=InlineKeyboardMarkup(
        inline_keyboard=[
            [button_add], [button_continue]
        ]
    )
    return keyboard


async def kb_add_and_del_learner() -> InlineKeyboardMarkup:
    """Инлайн клавиатура: 'Добавить ученика' и 'Удалить ученика'."""
    logging.info('kb_add_and_del_learner')

    button_add=InlineKeyboardButton(
        text='Добавить ученика',
        callback_data='add_token'
    )
    button_del=InlineKeyboardButton(
        text='Удалить ученика',
        callback_data='del_learner'
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [button_add], [button_del]
        ]
    )
    return keyboard


def kb_choise_learners(action: str, list_learners: list, back: int, forward: int, count: int, id_dz: int | None=None):
    """Клавиатура для выбора учеников для действий (удаления, выбора отправки дз)"""
    logging.info('kb_choise_learners')
    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_learners)
    whole = count_users // count
    remains = count_users % count
    max_forward = whole + 1
    # если есть остаток, то увеличиваем количество блоков на один, чтобы показать остаток
    if remains:
        max_forward = whole + 2
    if forward > max_forward:
        forward = max_forward
        back = forward - 2
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for learner in list_learners[back*count:(forward-1)*count]:
        text = learner.fio
        button = f'{action}!{id_dz}!{learner.id}' # action = delete_learner || action = send_dz
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'{action}back!{id_dz}!{str(back)}')
    button_count = InlineKeyboardButton(text=f'{back+1}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'{action}forward!{id_dz}!{str(forward)}')

    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)
    return kb_builder.as_markup()




def kb_delete_learner_after_confirm(postfix: str) -> InlineKeyboardMarkup:
    """Клавиатура для удаления ученика после подтверждения"""
    logging.info('kb_delete_learner_after_confirm')

    button_1 = InlineKeyboardButton(text='Да',
                                    callback_data=f"del_learner_confirm!{postfix}")
    button_2 = InlineKeyboardButton(text='Нет',
                                    callback_data='notdel_learner')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]],)
    return keyboard


async def kb_choise_name_dz(prefix, list_dz, back: int, forward: int, count: int, chapter: str | None=None):
    """Клавиатура для выбора названия ДЗ для различных действий"""
    logging.info('kb_choise_name_dz')
    tg_id = list_dz[0].tg_id
    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_dz)
    whole = count_users // count
    remains = count_users % count
    max_forward = whole + 1
    # если есть остаток, то увеличиваем количество блоков на один, чтобы показать остаток
    if remains:
        max_forward = whole + 2
    if forward > max_forward:
        forward = max_forward
        back = forward - 2
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    list_not_executed_dz = [dz for dz in await rq.get_dz_from_learner(tg_id_learner=tg_id) if not dz.executed_dz]
    name_not_executed_dz: list =[]
    for not_ex_dz in list_not_executed_dz:
        name_not_executed_dz.append(not_ex_dz.name_dz)
    for dz in list_dz[back*count:(forward-1)*count]:# прохожу по списку и беру id_dz
        if prefix == 'moi_dz':
            #list_not_executed_dz = [dz for dz in await rq.get_dz_from_learner(tg_id_learner=dz.tg_id) if not dz.executed_dz]
            if dz.name_dz not in name_not_executed_dz:
                text = f"{dz.name_dz} ✅" # к названию ДЗ добавить иконку ✅, если выполнено и ❌, если не выполнено
            else:
                text = f"{dz.name_dz} ❌"
        else:
            text = dz.name_dz

        # когда эта функция применяется в хэндреле learner_handler, нужен id_dz из таблицы RelationLearnerContent
        if prefix in ['moi_dz', 'choise_not_executed_dz']:
            id_dz = await rq.get_id_dz_from_id_relation(dz.id) # это из таблицы Relation ###или НАОБОРОТ
            button = f'{prefix}!{id_dz}!{dz.id}'# последнее из таблицы Content
        else:
            button = f'{prefix}!{dz.id}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'{prefix}back!{chapter}!{str(back)}')# ТУТ chapter!
    button_count = InlineKeyboardButton(text=f'{back+1}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'{prefix}forward!{chapter}!{str(forward)}')

    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)
    return kb_builder.as_markup()


async def kb_choise_name_dz_for_send_executed_dz(prefix, list_dz):
    """Клавиатура для выбора названия ДЗ для отправки выполненного ДЗ"""
    logging.info('kb_choise_name_dz_for_send_executed_dz')
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for dz in list_dz:# прохожу по списку и беру id_dz
        text = dz.name_dz

        # когда эта функция применяется в хэндреле learner_handler, нужен id_dz из таблицы RelationLearnerContent

        id_dz = await rq.get_id_dz_from_id_relation(dz.id) # это из таблицы Relation ###или НАОБОРОТ
        button = f'{prefix}!{id_dz}!{dz.id}'# последнее из таблицы Content

        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()



def kb_send_dz_to_learner() -> InlineKeyboardMarkup:
    """Клавиатура для отправки ДЗ ученику. Кнопки ДА, НЕТ"""
    logging.info('kb_send_dz_to_learner')

    button_1 = InlineKeyboardButton(text='Да',
                                    callback_data=f"press_yes_to_send_dz")
    button_2 = InlineKeyboardButton(text='Нет',
                                    callback_data='press_no_to_send_dz')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]],)
    return keyboard


def kb_learner_mayDZ_sendDZ() -> ReplyKeyboardMarkup:
    """Reply - клавиатура 'Мои ДЗ' и 'Отправить ДЗ на проверку' """

    logging.info('kb_learner_mayDZ_sendDZ')
    button_1 = KeyboardButton(text='Мои ДЗ')
    button_2 = KeyboardButton(text='Отправить ДЗ на проверку')

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1],[button_2]],
        resize_keyboard=True
    )
    return keyboard


def kb_all_right_check_dz(id_relation: int) -> InlineKeyboardMarkup:
    """инлайн кнопки 'Всё верно' и 'Исправить'"""
    logging.info('kb_all_right_check_dz')

    button_add=InlineKeyboardButton(
        text='Всё верно!',
        callback_data=f'all_right_dz!{id_relation}'
    )
    button_continue=InlineKeyboardButton(
        text='Исправить',
        callback_data=f'fix_dz!{id_relation}'
    )

    keyboard=InlineKeyboardMarkup(
        inline_keyboard=[
            [button_add], [button_continue]
        ]
    )
    return keyboard


def kb_check_dz_add_more_check_next() -> InlineKeyboardMarkup:
    """инлайн кнопки 'Добавить ещё' и 'Проверить следующее ДЗ'"""
    logging.info('kb_check_dz_add_more_check_next')

    button_add=InlineKeyboardButton(
        text='Добавить ещё',
        callback_data=f'add_more_check_dz'
    )
    button_continue=InlineKeyboardButton(
        text='Проверить следующее ДЗ',
        callback_data=f'check_next_dz'
    )

    keyboard=InlineKeyboardMarkup(
        inline_keyboard=[
            [button_add], [button_continue]
        ]
    )
    return keyboard


def kb_learner_begin() -> ReplyKeyboardMarkup:
    """Reply - клавиатура 'Отправить ДЗ на проверку' и 'Мои ДЗ' """

    logging.info('kb_learner_begin')
    button_1 = KeyboardButton(text='Отправить ДЗ на проверку')
    button_2 = KeyboardButton(text='Мои ДЗ')

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1],[button_2]],
        resize_keyboard=True
    )
    return keyboard

def kb_registration() -> InlineKeyboardMarkup:
    """инлайн кнопка 'Регистрация'"""
    logging.info('kb_registration')

    button_reg=InlineKeyboardButton(
        text='Регистрация',
        callback_data='registration'
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_reg]]
    )
    return keyboard