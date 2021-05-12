from fastapi import FastAPI

from common.db import create_session
from src.personal import get_personal_recommendations
from common.errors import UserNotFound, InvalidUUID


app = FastAPI()


@app.get('/user/{user_id}')
async def personal_recommendations(user_id) -> dict:
    """
    Список персональных рекомендаций фильмов
    :param user_id: id пользователя
    :return:
    """
    session = create_session()
    try:
        return {'result': get_personal_recommendations(session, user_id), 'error': None}
    except (UserNotFound, InvalidUUID) as e:
        return {'error': e.message, 'result': None}
