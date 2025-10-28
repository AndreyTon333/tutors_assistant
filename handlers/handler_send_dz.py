from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, default_state, StatesGroup
from aiogram.fsm.context import FSMContext
from datetime import datetime, date, timedelta

from aiogram.types import ReplyKeyboardRemove

from handlers.handler_add_dz import process_hello_admin
import keyboards.keyboards as kb
import database.requests as rq


router = Router()


import logging


dict_chapter: dict = {'EGE': 'ЕГЭ', 'EGE_variants': 'ЕГЭ (варианты)', 'OGE': 'ОГЭ', '10class': '10 класс', '9class': '9 класс', '8class': '8 класс'}

class SendDZ(StatesGroup):
    state_day_to_work = State()



@router.callback_query(F.data == 'send_dz')
async def process_send_dz(clb: CallbackQuery):
    """Обрабатывает нажатие inline кнопки 'Отправить ДЗ' в разделе 'Домашнее задание'. Выбераем раздел"""
    logging.info('process_send_dz')

    await clb.message.edit_text(text='Выберите раздел',
                                reply_markup=kb.kb_name_chapter_dz(prefix='process_send_dz_step1'))


@router.callback_query(F.data.startswith('process_send_dz_step1'))
async def process_send_dz_chapter(clb: CallbackQuery):
    """Обрабатывает нажатие inline кнопки выбранного раздела ДЗ"""
    logging.info(f'process_send_dz_chapter --- clb.data = {clb.data}')
    logging.info(f'process_send_dz_chapter --- my_tg_id = {clb.from_user.id}')

    #if len(clb.data.split('!'))==2:
     #   id_dz = clb.data.split('!')[-1]
    #elif len(clb.data.split('!'))==3:
    chapter = clb.data.split('!')[-1]

    # чтобы показать клавиатуру с названиями ДЗ, надо сформировать список с ДЗ из выбранного раздела
    list_dz = [dz for dz in await rq.get_id_dz_from_chapter(chapter=chapter)]
    if not list_dz:
        await clb.answer(text=f"Нет домашних заданий в разделе {dict_chapter[chapter]}", show_alert=True)
        return


    keyboard = await kb.kb_choise_name_dz(
        prefix=f'process_send_dz_step2',
        chapter=chapter, # НУЖЕН. id я возьму внутри функции при обходе списка ДЗ.
         #а chapter для информирования
        list_dz=list_dz,
        back=0,
        forward=2,
        count=6
    )
    await clb.message.edit_text(text=f"Выберите задание из раздела {dict_chapter[chapter]}",
                                reply_markup=keyboard)
    await clb.answer()

# >>>>
@router.callback_query(F.data.startswith('process_send_dz_step2forward'))
async def process_forward_choise_name_dz(clb: CallbackQuery) -> None:
    logging.info(f'process_forward_choise_name_dz --- clb.data = {clb.data}')

    chapter = clb.data.split('!')[-2]
    #id_dz = clb.data.split('!')[-2]
    #chapter = (await rq.get_name_dz(id_dz)).chapter
    #name_dz = (await rq.get_name_dz(id_dz)).name_dz

    list_dz = [dz for dz in await rq.get_id_dz_from_chapter(chapter=chapter)]
    if not list_dz:
        await clb.answer(text=f"Нет домашних заданий в разделе {dict_chapter[chapter]}", show_alert=True)
        return
    forward = int(clb.data.split('!')[-1]) + 1
    back = forward - 2

    keyboard = await kb.kb_choise_name_dz(
        prefix=f'process_send_dz_step2',
        chapter=chapter,
        list_dz=list_dz,
        back=back,
        forward=forward,
        count=6
    )
    try:
        await clb.message.edit_text(text=f"Выберитe задание из раздела {dict_chapter[chapter]}",
                                         reply_markup=keyboard)
    except:
        await clb.message.edit_text(text=f"Выберитe задание из разделa {dict_chapter[chapter]}",
                                         reply_markup=keyboard)
    await clb.answer()


# <<<<
@router.callback_query(F.data.startswith('process_send_dz_step2back'))
async def process_back_choise_name_dz(clb: CallbackQuery) -> None:
    logging.info(f'process_back_choise_name_dz --- clb.data = {clb.data}')

    chapter = clb.data.split('!')[-2]
    #id_dz = clb.data.split('!')[-2]
    #chapter = (await rq.get_name_dz(id_dz)).chapter

    list_dz = [dz for dz in await rq.get_id_dz_from_chapter(chapter=chapter)]
    if not list_dz:
        await clb.answer(text=f"Нет домашних заданий в разделе {dict_chapter[chapter]}", show_alert=True)
        return
    back = int(clb.data.split('!')[-1]) - 1
    forward = back + 2

    keyboard = await kb.kb_choise_name_dz(
        prefix=f'process_send_dz_step2',
        chapter=chapter,
        list_dz=list_dz,
        back=back,
        forward=forward,
        count=6
    )
    try:
        await clb.message.edit_text(text=f"Выберитe задание из раздела {dict_chapter[chapter]}",
                                         reply_markup=keyboard)
    except:
        await clb.message.edit_text(text=f"Выберитe задание из разделa {dict_chapter[chapter]}",
                                         reply_markup=keyboard)
    await clb.answer()


@router.callback_query(F.data.startswith('process_send_dz_step2'))
async def process_send_dz_name_dz(clb: CallbackQuery):
    """Срабатывает на inline кнопку выбранного раздела ДЗ"""
    logging.info(f'process_send_dz_name_dz --- clb.data = {clb.data}')
    id_dz = clb.data.split('!')[-1]
    chapter = (await rq.get_name_dz(id_dz)).chapter
    #chapter = clb.data.split('!')[-2]

    list_learners = [learner for learner in await rq.get_all_learners()]
    if not list_learners:
        #await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id)
        await clb.answer(text='Нет учеников для отправки домашнего задания', show_alert=True)
        return
    # name_dz функция, которая выдает название задания по его id
    name_dz = (await rq.get_name_dz(id_dz)).name_dz
    keyboard = kb.kb_choise_learners(
        action='process_send_dz_step3',
        list_learners=list_learners,
        id_dz=id_dz,
        back=0,
        forward=2,
        count=6)
    await clb.message.edit_text(text=f"Выберитe ученика, которому нужно отправить задание {dict_chapter[chapter]}/{name_dz}",
                                reply_markup=keyboard)
                                #reply_markup=kb.kb_name_chapter_dz(prefix=f'process_send_dz_step2!{chapter}'))


# >>>>
@router.callback_query(F.data.startswith('process_send_dz_step3forward'))
async def process_forward(clb: CallbackQuery) -> None:
    logging.info(f'process_send_dzforward: {clb.data}')

    id_dz = clb.data.split('!')[-2]
    name_dz = (await rq.get_name_dz(id=id_dz)).name_dz
    chapter = (await rq.get_name_dz(id=id_dz)).chapter
    list_learners = [learner for learner in await rq.get_all_learners()]
    forward = int(clb.data.split('!')[-1]) + 1
    back = forward - 2
    keyboard = kb.kb_choise_learners(action='process_send_dz_step3', id_dz=id_dz, list_learners=list_learners, back=back, forward=forward, count=6)
    try:
        await clb.message.edit_text(text=f"Выберитe ученика, которому нужно отправить задание:  {dict_chapter[chapter]}/{name_dz}",
                                         reply_markup=keyboard)
    except:
        await clb.message.edit_text(text=f"Выберитe ученика, которому нужно отправить зaдание: {dict_chapter[chapter]}/{name_dz}",
                                         reply_markup=keyboard)
    await clb.answer()


# <<<<
@router.callback_query(F.data.startswith('process_send_dz_step3back'))
async def process_back(clb: CallbackQuery) -> None:
    logging.info(f'process_send_dzback: {clb.data}')

    id_dz = clb.data.split('!')[-2]
    name_dz = (await rq.get_name_dz(id=id_dz)).name_dz
    chapter = (await rq.get_name_dz(id=id_dz)).chapter
    list_learners = [learner for learner in await rq.get_all_learners()]
    back = int(clb.data.split('!')[-1]) - 1
    forward = back + 2
    keyboard = kb.kb_choise_learners(action='process_send_dz_step3', id_dz=id_dz, list_learners=list_learners, back=back, forward=forward, count=6)
    try:
        await clb.message.edit_text(text=f"Выберитe ученика, которому нужно отправить задание:  {dict_chapter[chapter]}/{name_dz}",
                                         reply_markup=keyboard)
    except:
        await clb.message.edit_text(text=f"Выберитe ученика, которому нужно отправить задание: {dict_chapter[chapter]}/{name_dz}",
                                         reply_markup=keyboard)
    await clb.answer()


@router.callback_query(F.data.startswith('process_send_dz_step3'))
async def process_send_dz_choise_learner(clb: CallbackQuery, state: FSMContext) -> None:
    """Перевод в режим ожидания получения количества дней на выполнение ДЗ"""
    logging.info(f'process_send_dz_choise_learner --- clb.data = {clb.data}')

    id_learner = clb.data.split('!')[-1]
    id_dz = clb.data.split('!')[-2]

    data_dz = await rq.get_name_dz(id=id_dz)
    chapter = data_dz.chapter
    name_dz = data_dz.name_dz
    fio = (await rq.get_learner_id(id=id_learner)).fio
    tg_id = (await rq.get_learner_id(id=id_learner)).tg_id

    await state.set_state(SendDZ.state_day_to_work)
    await state.update_data(chapter=chapter)
    await state.update_data(name_dz=name_dz)
    await state.update_data(fio=fio)
    await state.update_data(tg_id=tg_id)
    await state.update_data(id_dz=id_dz)

    await clb.message.edit_text(
        text=f"Пришлите количество дней на выполнение задания {dict_chapter[chapter]}/{name_dz} ученику {fio}"
    )

@router.message(SendDZ.state_day_to_work)
async def process_send_dz_send_day_to_work(message: Message, bot: Bot, state: FSMContext):
    """Сохранение количества дней на выполнение ДЗ. Инлайн клавиатура Отправить задание 'ДА', 'НЕТ'"""
    logging.info('process_send_dz_send_day_to_work')

    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)


    #модуль с датой
    days_to_work = message.text

    current_date = date.today()
    dead_line = current_date + timedelta(days=int(days_to_work))
    dead_line_format = dead_line.strftime('%d-%m-%Y')

    await state.update_data(deadline=dead_line_format)
    data_state = await state.get_data()

    list_ = [data for data in data_state]
    logging.info(f"list(data_state) = {list_} ---- data_state = {data_state}")



    keyboard = kb.kb_send_dz_to_learner()
    await message.answer(
        text=f"Отправить задание: {dict_chapter[data_state['chapter']]}/{data_state['name_dz']} ученику {data_state['fio']}.\n"
        f"Срок выполнения задания до {dead_line_format} ",
        reply_markup=keyboard
    )



@router.callback_query(F.data == 'press_no_to_send_dz')
async def process_press_no_to_send_dz(clb: CallbackQuery, state:FSMContext, bot:Bot):
    """Нажатие кнопки 'НЕТ' и отмена отправки ДЗ ученику"""
    logging.info(f"process_press_no_to_send_dz --- state.get_data() = {await state.get_data()}")

    await state.clear()
    await state.set_state(state=None)
    await clb.answer(text='Отправка задания отменена', show_alert=True)
    await bot.delete_message(
        chat_id=clb.message.chat.id,
        message_id=clb.message.message_id
    )
    await process_hello_admin(message=clb.message, state=state, bot=bot)



@router.callback_query(F.data == 'press_yes_to_send_dz')
async def process_press_yes_to_send_dz(clb: CallbackQuery, state:FSMContext, bot:Bot):
    """Нажатие кнопки 'ДА' и отправка ДЗ ученику"""
    logging.info(f"process_press_yes_to_send_dz --- state.get_data() = {await state.get_data()}")

    data_state = await state.get_data()
    #current_date = date.today()
    #current_date = datetime.strptime(current_date_str, '%Y-%m-%d')
    #dead_line = (current_date + timedelta(days=int(data_state['days_to_work']))).strftime('%d-%m-%Y')

    relation_learners_content = {'tg_id': data_state['tg_id'], 'fio': data_state['fio'],
                                 'id_dz': data_state['id_dz'], 'deadline': data_state['deadline'],
                                 'name_dz': data_state['name_dz']}
    await rq.add_relation_lerners_content(relation_lerners_content=relation_learners_content)

    # оповещение ученика о новом ДЗ  И ОТПРАВКА УЧЕНИКУ КОНТЕНТА С ДЗ
    data_content = await rq.get_name_dz(id=data_state['id_dz'])  # data_content из таблицы Content
    comment_dz_to_execute = data_content.text
    dz_to_execute = data_content.content

    if comment_dz_to_execute: # если есть комменты к ДЗ, то отправляем сперва комента, затем ссылки
        if ',!?!,' in comment_dz_to_execute:
                #list_comment_dz_to_execute = comment_dz_to_execute.split(',!?!,')

            list_comment_dz_to_execute = comment_dz_to_execute.split(',!?!,')
            for item in list_comment_dz_to_execute:
                if 'https://' not in item: # сперва выводим комменты к ДЗ
                    await bot.send_message(chat_id=data_state['tg_id'], text=item)
            for item in list_comment_dz_to_execute:
                if 'https://' in item: # затем выводим тексты ссылок
                    await bot.send_message(chat_id=data_state['tg_id'], text=item)

    if dz_to_execute:
        list_dz_to_execute = dz_to_execute.split(',')

        for item in list_dz_to_execute:
            try:
                await bot.send_photo(chat_id=data_state['tg_id'], photo=item)
            except:
                try:
                    await bot.send_document(chat_id=data_state['tg_id'], document=item)
                except:
                    try:
                        await bot.send_message(chat_id=data_state['tg_id'], link_preview_options=True) # добавить Linkpreviewoption
                    except:
                        pass


    keyboard = kb.kb_learner_mayDZ_sendDZ()
    await bot.send_message(
        chat_id=data_state['tg_id'],
        text=f"Вы получили домашнее задание {data_state['name_dz']}, срок выполнения {data_state['deadline']}",
        reply_markup=keyboard
    )

    await clb.answer(
        text=f"Домашнее задание {dict_chapter[data_state['chapter']]}/{data_state['name_dz']} со сроком выполнения "
        f"до {data_state['deadline']} успешно отправлено ученику {data_state['fio']}",
        show_alert=True
    )
    await bot.delete_message(
        chat_id=clb.message.chat.id,
        message_id=clb.message.message_id
    )
    await state.clear()


async def process_scheduler(bot: Bot):
    """в 10 утра запускается планировкщик задач и если до deadline осталось меньше 1 дня отправляем напоминание
    Для этого - захожу с талицу Relation, выбираю невыполненные ДЗ, проверяю сколько до deadline, отправляю пользователям"""
    logging.info('process_scheduler')

    data_relation = await rq.get_all_relation()
    list_dz_one_day_to_deadline: list =[]
    current_day = date.today().strftime('%d-%m-%Y')
    date_format = '%d-%m-%Y'
    for row_data_relation in data_relation:
        # если пусто в excuted_dz и в comment_executed_dz или (пусто в executed_dz и в comment_executed_dz не "https"
        if (not row_data_relation.executed_dz and not row_data_relation.comment_executed_dz) or (not row_data_relation.executed_dz and 'https' not in row_data_relation.comment_executed_dz):
            day_to_deadline = datetime.strptime(row_data_relation.deadline, date_format) - datetime.strptime(current_day, date_format)

            logging.info(f"day_to_deadline = {day_to_deadline}")

            # если до deadline меньше дня
            if day_to_deadline.days == 1:
                list_dz_one_day_to_deadline.append(row_data_relation) ### это не надо
                # отправка пользователю сообщения о deadline
                await bot.send_message(
                    chat_id=row_data_relation.tg_id,
                    text=f'Вы получили домашнее задание "{row_data_relation.name_dz}", срок выполнения {row_data_relation.deadline}'
                )

                logging.info(f"{row_data_relation.id}")
