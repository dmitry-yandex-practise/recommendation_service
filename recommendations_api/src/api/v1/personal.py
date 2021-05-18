from fastapi import APIRouter, Depends

from services.personal import get_personal_service
from common.errors import UserNotFound, InvalidUUID


router = APIRouter()


@router.get('/{user_id}')
async def personal_recommendations(user_id, service=Depends(get_personal_service)) -> dict:
    """
    Список персональных рекомендаций фильмов
    :param user_id: id пользователя,
    :param service: сервис
    :return:
    """
    try:
        recommendations = await service.get_personal_recommendations(user_id)
        return {'result': recommendations, 'error': None}
    except (UserNotFound, InvalidUUID) as e:
        return {'error': e.message, 'result': None}
