from database.models import Learners, Content, RelationLernersContent
from database.models import async_session
from sqlalchemy import select, update, delete

import logging


### LEARNERS

async def add_token(data: dict):
    """Добавление токена в БД"""
    logging.info('add_token')
    async with async_session() as session:
        session.add(Learners(**data))
        await session.commit()

async def add_learner(data: dict):
    """Добавление ученика в БД"""
    logging.info('add_learner')
    token = data['token']
    async with async_session() as session:
        learner = await session.scalar(select(Learners).where(Learners.token == token))
        learner.tg_id = data['tg_id']
        learner.username = data['username']
        learner.fio = data['fio']
        await session.commit()

async def get_all_learners()-> Learners:
    """Получение всех учеников, зарегистрированных в боте"""
    logging.info('get_all_learners')
    async with async_session() as session:
        learners = await session.scalars(select(Learners).where(Learners.fio != ''))
        return learners



async def get_learner_id(id: int) -> Learners:
    """Получаем информацию по ученику"""
    logging.info(f'get_learner_id')
    async with async_session() as session:
        learner = await session.scalar(select(Learners).where(Learners.id == id))
        return learner


async def delete_learner(id: int) -> None:
    """Удаляет ученика по id"""
    logging.info('delete_learner')
    async with async_session() as session:
        learner = await session.scalar(select(Learners).where(Learners.id == id))
        await session.delete(learner)
        await session.commit()

async def is_learner_in_database(tg_id: int) -> bool:
    """Возвращает True, если ученик есть в БД"""
    logging.info('is_learner_in_database')
    async with async_session() as session:
        learner = await session.scalar(select(Learners).where(Learners.tg_id == tg_id))
        logging.info(f"learner = {learner}")
        if learner:
            return True
        return False


async def is_token_valid(token: int) -> bool:
    """возвращает True, если токен есть в БД и поле 'ФИО' пусто"""
    logging.info('is_token_valid')
    async with async_session() as session:
        token_in_DB:Learners = await session.scalar(select(Learners).where(Learners.token == token))
        if token_in_DB and not token_in_DB.fio: # True если токен есть в БД и не занят другим пользователем
            return True
        return False

async def get_learner_data_from_tg_id(tg_id: int) -> Learners:
    """Возвращает data строки из таблицы Learner по tg_id"""
    logging.info('get_learner_data_from_tg_id')
    async with async_session() as session:
        learner = await session.scalar(select(Learners).where(Learners.tg_id == tg_id))
        return learner

### CONTENT

async def add_content(content: dict) -> Content:
    """Дабавляет домашнее задание в БД"""
    logging.info('add_content')
    async with async_session() as session:
        session.add(Content(**content))
        await session.commit()

async def get_id_dz_from_chapter(chapter: str) -> Content:
    """Возвращает id домашних заданий с выбранного раздела"""
    logging.info('get_id_dz_from_chapter')
    async with async_session() as session:
        id_dz = await session.scalars(select(Content).where(Content.chapter == chapter))
        return id_dz


async def get_name_dz(id: int) -> Content:
    """Возвращает строку домашнего задания по его id"""
    logging.info('get_name_dz')
    async with async_session() as session:
        data_dz = await session.scalar(select(Content).where(Content.id == id))
        return data_dz



### RelationLernersContent

async def add_relation_lerners_content(relation_lerners_content: dict) ->RelationLernersContent:
    """Добавляет в тавблицу relation_lerners_content данные"""
    logging.info('add_relation_lerners_content')
    async with async_session() as session:
        session.add(RelationLernersContent(**relation_lerners_content))
        await session.commit()


async def get_all_relation() -> RelationLernersContent:
    """Возвращает всю таблицу Relation"""
    logging.info('get_all_relation')
    async with async_session() as session:
        data_all_relation = await session.scalars(select(RelationLernersContent))
        return data_all_relation


async def get_count_executed_dz()-> int:
    """Получение количества непроверенных домашних заданий"""
    logging.info('get_count_executed_dz')
    async with async_session() as session:
        data_dz = await session.scalars(select(RelationLernersContent))#.where(((RelationLernersContent.executed_dz != '') or (RelationLernersContent.comment_executed_dz != '')) and RelationLernersContent.checked_dz == ''))
        list_dz = [row for row in data_dz]
        count_dz_to_check: int = 0
        for elem in list_dz:
            if (elem.executed_dz != '' or elem.comment_executed_dz != '') and elem.checked_dz == '':
                #logging.info(f" elem.executed_dz = {elem.executed_dz} --- elem.comment_executed_dz = {elem.comment_executed_dz} --- elem.checked_dz = {elem.checked_dz}")
                count_dz_to_check += 1
                #logging.info(f" count_dz_to_check {count_dz_to_check}")

        #list_for_example = [elem for elem in await session.scalars(select(RelationLernersContent).where(RelationLernersContent.executed_dz != '',
        #                                                                     RelationLernersContent.checked_dz != ''))]

        #logging.info(f'list_for_example = {list_for_example}')
       # logging.info(f'data_dz = {data_dz} ------- list_dz = {list_dz}')
        #count_dz_to_check = len(list_dz)
        return count_dz_to_check


async def get_dz_to_executed()-> list:
    """Получение tg_id, fio, id_dz, deadline"""
    logging.info('get_dz_to_executed')
    async with async_session() as session:
        data_dz = await session.scalars(select(RelationLernersContent))
        list_dz = [row for row in data_dz]
        list_return: list = []
        for elem in list_dz:
            if (elem.executed_dz != '' or elem.comment_executed_dz != '') and elem.checked_dz == '':
                #logging.info(f" elem.executed_dz = {elem.executed_dz} --- elem.comment_executed_dz = {elem.comment_executed_dz} --- elem.checked_dz = {elem.checked_dz}")
                list_return.append(elem)
        return list_return



async def get_dz_from_learner(tg_id_learner: int) -> RelationLernersContent:
    """Возвращает все id ДЗ ученика по его tg_id"""
    logging.info('get_dz_from_learner')
    async with async_session() as session:
        id_dz = await session.scalars(select(RelationLernersContent).where(RelationLernersContent.tg_id == tg_id_learner))
        return id_dz


async def get_id_dz_from_id_relation(id: int) -> int:
    """Функция возвращает id_dz по id из таблицы RelationLearnerContent"""
    logging.info('get_id_dz_from_id_relation')
    async with async_session() as session:
        data_id_dz = await session.scalar(select(RelationLernersContent).where(RelationLernersContent.id == id))
        id_dz = data_id_dz.id_dz
        return id_dz


async def get_data_relation_from_id(id: int) -> RelationLernersContent:
    """Функция возвращает data_relation по id из таблицы RelationLearnerContent"""
    logging.info('get_data_relation_from_id')
    async with async_session() as session:
        data_relation = await session.scalar(select(RelationLernersContent).where(RelationLernersContent.id == id))
        return data_relation

async def set_attribute_relation(id_relation: int, attribute: str, set_attribute: str) -> None:
    """Установка значения в табличу Relation"""
    logging.info('set_attribute_relation')

    async with async_session() as session:
        data_relation = await session.scalar(select(RelationLernersContent).where(RelationLernersContent.id == id_relation))

        if attribute == 'comment_to_execute_dz':
            data_relation.comment_to_execute_dz = set_attribute
        elif attribute == 'executed_dz':
            data_relation.executed_dz = set_attribute
        elif attribute == 'comment_executed_dz':
            data_relation.comment_executed_dz = set_attribute
        elif attribute == 'checked_dz':
            data_relation.checked_dz = set_attribute
        elif attribute == 'comment_checked_dz':
            data_relation.comment_checked_dz = set_attribute

        await session.commit()
