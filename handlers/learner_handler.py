from aiogram import F, Router, Bot

from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, default_state, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
from config_data.config import Config, load_config

from handlers.handler_add_dz import process_hello_admin


import keyboards.keyboards as kb
import database.requests as rq


router = Router()

storage = MemoryStorage()

import logging
import asyncio
import random

class LearnerFSM(StatesGroup):
    state_send_dz = State()
    #state_fio = State()


@router.message(F.text == 'Мои ДЗ')
async def process_press_button_moi_dz(message:Message, bot:Bot):
    """Срабатывает на reply кнопку 'Мои ДЗ'"""
    logging.info('process_press_button_moi_dz')

    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)


    # чтобы показать клавиатуру с названиями ДЗ, надо сформировать список с ДЗ из выбранного раздела
    list_dz = [dz for dz in await rq.get_dz_from_learner(tg_id_learner=message.chat.id)]
    ###list_dz_sorted = list_dz.sort(key=)
    if not list_dz:
        await message.answer(text=f"У вас нет домашних заданий.")
        return
    logging.info(list_dz)
    keyboard = await kb.kb_choise_name_dz(
        prefix='moi_dz',
        list_dz=list_dz,
        back=0,
        forward=2,
        count=6,
        #chapter=tg_id_learner #возможно понадобится тг ид ученика
    )
    await message.answer(text='Выберите задания.',
                         reply_markup=keyboard)




# >>>>
@router.callback_query(F.data.startswith('moi_dzforward'))
async def process_forward_choise_name_dz_from_learner(clb: CallbackQuery) -> None:
    logging.info(f'process_forward_choise_name_dz_from_learner --- clb.data = {clb.data}')

    #chapter = clb.data.split('!')[-2]
    #id_dz = clb.data.split('!')[-2]
    #chapter = (await rq.get_name_dz(id_dz)).chapter
    #name_dz = (await rq.get_name_dz(id_dz)).name_dz
    tg_id=clb.message.chat.id
    list_dz = [dz for dz in await rq.get_dz_from_learner(tg_id_learner=tg_id)]
    #if not list_dz:
     #   await clb.answer(text=f"Нет домашних заданий в разделе {dict_chapter[chapter]}", show_alert=True)
      #  return
    forward = int(clb.data.split('!')[-1]) + 1
    back = forward - 2

    keyboard = await kb.kb_choise_name_dz(
        prefix=f'moi_dz',
        #chapter=chapter,
        list_dz=list_dz,
        back=back,
        forward=forward,
        count=6
    )
    try:
        await clb.message.edit_text(text=f"Выберитe задание",
                                         reply_markup=keyboard)
    except:
        await clb.message.edit_text(text=f"Выберитe заданиe ",
                                         reply_markup=keyboard)
    await clb.answer()


# <<<<
@router.callback_query(F.data.startswith('moi_dzback'))
async def process_back_choise_name_dz_from_learner(clb: CallbackQuery) -> None:
    logging.info(f'process_back_choise_name_dz_from_learner --- clb.data = {clb.data}')

    #chapter = clb.data.split('!')[-2]
    #id_dz = clb.data.split('!')[-2]
    #chapter = (await rq.get_name_dz(id_dz)).chapter
    tg_id = clb.message.chat.id
    list_dz = [dz for dz in await rq.get_dz_from_learner(tg_id_learner=tg_id)]
    #if not list_dz:
     #   await clb.answer(text=f"Нет домашних заданий в разделе {dict_chapter[chapter]}", show_alert=True)
      #  return
    back = int(clb.data.split('!')[-1]) - 1
    forward = back + 2


    keyboard = await kb.kb_choise_name_dz(
        prefix=f'moi_dz',
        #chapter=chapter,
        list_dz=list_dz,
        back=back,
        forward=forward,
        count=6
    )
    try:
        await clb.message.edit_text(text=f"Выберитe задание",
                                         reply_markup=keyboard)
    except:
        await clb.message.edit_text(text=f"Выберитe заданиe ",
                                         reply_markup=keyboard)
    await clb.answer()


@router.callback_query(F.data.startswith('moi_dz'))
async def process_take_dz_from_learner(clb: CallbackQuery, bot: Bot):
    """Срабатывает на inline кнопку выбранного ДЗ"""
    logging.info(f'process_take_dz_from_learner --- clb.data = {clb.data}')

    tg_id = clb.message.chat.id
    id_content = clb.data.split('!')[-2]
    id_relation = clb.data.split('!')[-1]


    data_relation = await rq.get_data_relation_from_id(id=int(id_relation)) # data_ из таблицы Relation

    data_content = await rq.get_name_dz(id=int(id_content))  # data_ из таблицы Content

    deadline = data_relation.deadline
    name_dz = data_relation.name_dz

    dz_to_execute = data_content.content
    comment_dz_to_execute = data_content.text




    # СПЕРВА отправляем .text и .content из таблицы Content
    await clb.message.answer(
        text= f"Домашнее задание {name_dz},\nсрок выполнения - {deadline}"
    )

    if comment_dz_to_execute: # если есть комменты к ДЗ, то отправляем сперва комента, затем ссылки
        if ',!?!,' in comment_dz_to_execute:
                #list_comment_dz_to_execute = comment_dz_to_execute.split(',!?!,')

            list_comment_dz_to_execute = comment_dz_to_execute.split(',!?!,')
            for item in list_comment_dz_to_execute:
                if 'https://' not in item: # сперва выводим комменты к ДЗ
                    await bot.send_message(chat_id=tg_id, text=item)
            for item in list_comment_dz_to_execute:
                if 'https://' in item: # затем выводим тексты ссылок
                    await bot.send_message(chat_id=tg_id, text=item)



    if dz_to_execute:
        list_dz_to_execute = dz_to_execute.split(',')

        for item in list_dz_to_execute:
            try:
                await bot.send_photo(chat_id=tg_id, photo=item)
            except:
                try:
                    await bot.send_document(chat_id=tg_id, document=item)
                except:
                    try:
                        await bot.send_message(chat_id=tg_id, link_preview_options=True) # добавить Linkpreviewoption
                    except:
                        pass

    logging.info(f"id_conect = {id_content} --- id_relation = {id_relation} --- name_dz = {name_dz} --- deadline = {deadline} ---- dz_to_execute = {dz_to_execute} --- list_dz_to_execute = {list_dz_to_execute}")
    # ЗАТЕМ отправить правки по ДЗ, если они есть. Правки в таблице Relation в колонке checked_dz
    # Коментарий к исправленному заданию 1,!?!,AgACAgIAAxkBAAIIoGc16pgsf9tM-xGPJekpfG_JupfsAAK46zEbi26xSVqDzosTEAhZAQADAgADeAADNgQ,
    # AgACAgIAAxkBAAIIn2c16pjHLLC4nmEReikkHFLKWOrrAAK36zEbi26xSQimGt3NxewlAQADAgADeQADNgQ,AgACAgIAAxkBAAIIoWc16phedBzSXbaH9LRSqkNd2qVzAAK56zEbi26xSWzI27vsCBOyAQADAgADeAADNgQ

    checked_dz = data_relation.checked_dz
    comment_checked_dz = data_relation.comment_checked_dz
    logging.info(f'checked_dz = {checked_dz} --- comment_checked_dz = {comment_checked_dz}')
    if checked_dz or comment_checked_dz:
        logging.info('if checked_dz or comment_checked_dz:')
        if checked_dz == 'Всё верно':
            logging.info("if checked_dz == 'Всё верно':")
            await clb.message.answer(
                text= f"Домашнее задание {name_dz} проверено преподавателем. \nВсё выполнено верно!"
            )
            return

        if (checked_dz or comment_checked_dz) and checked_dz != 'Всё верно': # Если есть реальный контент от учителя, то сперва отправляем это сообщение
            logging.info("if (checked_dz or comment_checked_dz) and checked_dz != 'Всё верно':")
            await clb.message.answer(
                text= f'Материалы проверки ДЗ "{name_dz}", полученные от преподавателя'
            )

        if comment_checked_dz: # если есть комменты к проверенному ДЗ, то отправляем сперва комента, затем ссылки
            logging.info("if comment_checked_dz")
            if ',!?!,' in comment_checked_dz:
                logging.info("if ',!?!,' in comment_checked_dz:")
                list_comment_checked_dz = comment_checked_dz.split(',!?!,')
            else:
                list_comment_checked_dz = [comment_checked_dz]
            for item in list_comment_checked_dz:
                if 'https://' not in item: # сперва выводим комменты к ДЗ
                    await bot.send_message(chat_id=tg_id, text=item)
            for item in list_comment_checked_dz:
                if 'https://' in item: # затем выводим тексты ссылок
                    await bot.send_message(chat_id=tg_id, text=item)

        if checked_dz:
            logging.info("if checked_dz:")
            list_checked_dz: list =[]
            if ',' in checked_dz:
                logging.info("if ',' in checked_dz:")
                list_checked_dz = checked_dz.split(',')
            else:
                logging.info("else:")
                list_checked_dz = [checked_dz]
            logging.info(f"list_checked_dz = {list_checked_dz}")
            for item in list_checked_dz:
                try:
                    await bot.send_photo(chat_id=tg_id, photo=item)
                except:
                    try:
                        await bot.send_document(chat_id=tg_id, document=item)
                    except:
                        try:
                            await bot.send_message(chat_id=tg_id, link_preview_options=True) # добавить Linkpreviewoption
                        except:
                            pass


    await clb.answer()



# ОТПРАВИТЬ ДЗ НА ПОРВЕРКУ
@router.message(F.text == 'Отправить ДЗ на проверку')
async def process_press_button_send_dz(message:Message, bot:Bot, state: FSMContext):
    """Срабатывает на reply кнопку 'Отправить ДЗ на проверку'"""
    logging.info('process_press_button_send_dz')

    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)

    #### Сделать проверку на наличие невыполненного ДЗ. Если нет - return. Если есть,
    ### то показать список ДЗ на которое надо ответить отправкой ДЗ
    tg_id = message.chat.id
    list_dz = [dz for dz in await rq.get_dz_from_learner(tg_id_learner=tg_id)]
    list_not_executed_dz = [dz for dz in await rq.get_dz_from_learner(tg_id_learner=tg_id) if not dz.executed_dz]
    #logging.info(f" list_dz = {list_dz} --- list_not_executed_dz = {list_not_executed_dz} --- {(list_not_executed_dz[0]).name_dz}")

    #a = [i for i in (int(input()) for _ in range(5)) if i % 10 == 0]
#    ---------- ================================ --------------
#        ^          читаем пять целых чисел            ^
#        |                                             |
#        -----------------------------------------------
#                   отбираем кратные десяти



    if not list_dz: # если нет ДЗ
        await message.answer(text=f"У вас нет домашних заданий.")
        return
    elif not list_not_executed_dz:
        await message.answer(text=f"У вас нет невыполненных домашних заданий.")
        return
    else:
        keyboard=await kb.kb_choise_name_dz_for_send_executed_dz(
            prefix='choise_not_executed_dz', # префикс для следующего хендлера
            list_dz=list_not_executed_dz # это не список, а карутина
        )
        await message.answer(
            text=f"Выберите из списка невыполненных домашних заданий то,\nпо которому хотите прислать контент.",
            reply_markup=keyboard)




@router.callback_query(F.data.startswith('choise_not_executed_dz'))
async def process_set_state_send_execute_dz(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Срабатывает на inline кнопку выбранного названия ДЗ, устанавливает состояние ожидания контента выполненного ДЗ"""
    logging.info(f'process_set_state_send_execute_dz --- clb.data = {clb.data}')

    # из колбэка сохранить id таблицы Relation, чтобы знать на какое ДЗ отвечают
    id_relation = clb.data.split('!')[-1]
    await state.update_data(id_relation=id_relation) #сохранение id таблицы relation

    # переход в состояние ожидания контента
    await state.set_state(state=LearnerFSM.state_send_dz)
    await clb.message.answer(
        text=f"Пришлите контент выполненного домашнего задания 📎. \nКонтент может быть текстом с сылками, фотографиями или файлом.\n\n"
        f"Если вы хотите прислать текстовый комментарий к домашнему заданию, пришлите его первым отдельным сообщением,"
        f" не прикрепляя к фотографии или файлу.")
    await clb.answer()



@router.message(LearnerFSM.state_send_dz)
async def process_send_executed_dz(message: Message, bot: Bot, state: FSMContext):
    """Получение и сохранение выполненного ДЗ, предложение отправить еще"""
    logging.info('process_send_executed_dz')


    #logging.info(f"state.get_data = {await state.get_data()}")

    await asyncio.sleep(random.random())

    data = await state.get_data()
    list_executed_dz = data.get('executed_dz', [])  # метод get у словаря: если есть ключ 'executed_dz', то выдаст его, если нет, то пустой список
    count = data.get('count', [])
    #logging.info(f"STROKA 243 --- list_executed_dz = {list_executed_dz} ---- count = {count}")

    if message.text:
        # получаем что есть в state data.text
        data_text = await state.get_data()
        if 'comment_executed_dz' not in data_text:
            await state.update_data(comment_executed_dz=message.text)
        else:
            data_text_new = data_text['comment_executed_dz'] + ',!?!,' + message.text
            await state.update_data(comment_executed_dz=data_text_new)

        await message.answer(text='Пришлите контент для задания 📎')
        #print(1, message.html_text)
        #print(2, message.text)
        #await message.answer(text=f"message.text = {message.text} \n------- message.html_text {message.html_text}")
        return

    elif message.photo:
        executed_dz = message.photo[-1].file_id

    elif message.document:
        executed_dz = message.document.file_id


    list_executed_dz.append(executed_dz)
    count.append(executed_dz)

    logging.info(f"executed_dz = {executed_dz} --- list_executed_dz = {list_executed_dz} --- count = {count}")

    await state.update_data(executed_dz=list_executed_dz)
    await state.update_data(count=count)
    await state.set_state(state=None)

    #logging.info(f"--- content = {content} --- list_content = {list_content} ")
    #await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


    if len(count) == 1:
        await message.answer(
        text='Вы можете добавить контент к проверенному домашнему заданию, для этого нажмите "Добавить ещё", а можете загрзить его в базу данных.',
        reply_markup=kb.kb_save_add_dz(endfix='send_executed_dz'))



@router.callback_query(F.data.endswith('send_executed_dz'))
async def process_send_executed_dz_add_dz_written_content_to_bd(clb: CallbackQuery, state: FSMContext, bot: Bot):
    logging.info(f'process_send_executed_dz_add_dz_written_content_to_bd {clb.message.chat.id}')

    answer = clb.data.split('!')[0]
    tg_id = clb.message.chat.id

    if answer == 'add_more':
        await state.set_state(LearnerFSM.state_send_dz)
        await state.update_data(count=[])
        await clb.message.edit_text(
            text='Пришлите контент для задания 📎')

    elif answer == 'continue':
        # если контент не будут добавлять, только текст, то будет ошибка
        data_executed_dz = await state.get_data()
        logging.info(data_executed_dz)

        if 'executed_dz' in data_executed_dz or 'comment_executed_dz' in data_executed_dz:
            if 'executed_dz' in data_executed_dz:
                data_list_executed_dz = (await state.get_data())['executed_dz']
                str_executed_dz = ','.join(data_list_executed_dz)
                logging.info(f"data_list_executed_dz = {data_list_executed_dz} --- str_executed_dz = {str_executed_dz}")
                # установка строки в БД с контентом
                await rq.set_attribute_relation(id_relation=data_executed_dz['id_relation'],
                                                attribute='executed_dz',
                                                set_attribute=str_executed_dz)
            if 'comment_executed_dz' in data_executed_dz:
                comment_executed_dz = (await state.get_data())['comment_executed_dz']
                logging.info(f" comment_executed_dz = {comment_executed_dz}")
                await rq.set_attribute_relation(id_relation=data_executed_dz['id_relation'],
                                                attribute='comment_executed_dz',
                                                set_attribute=comment_executed_dz)
            logging.info(f"--- await state.get_data() = {await state.get_data()} ")
            await state.clear()
            await state.set_state(state=None)

            await clb.message.answer(
                text='Домашнее задание успешно отправлено на проверку'
            )

            fio = (await rq.get_learner_data_from_tg_id(tg_id=tg_id)).fio
            config: Config = load_config()
            id_admin = config.tg_bot.admin_ids
            await bot.send_message(
                chat_id=id_admin,
                text=f'Получено выполненное ДЗ от ученика {fio}'#,
                #reply_markup=kb.kb_admin_dz_lrn()
            )

        else:
            await clb.message.answer(
                text='Добавте контент к домашнему заданию'
            )
            await process_set_state_send_execute_dz(clb=clb, state=state, bot=bot)
        await clb.answer()