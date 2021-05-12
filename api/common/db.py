from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from common.settings import RECOMMENDATIONS_DB


def create_session(db=RECOMMENDATIONS_DB):
    """
    Сессия подключения к БД
    :param db: адрес БД
    :return:
    """
    engine = create_engine(db)
    Session = sessionmaker(bind=engine)
    session = Session()

    return session


