from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status

from api.v1.models import User
from services.user import UserService, get_user_service

router = APIRouter()


@router.get('/{user_id}', response_model=User)
async def user_details(
        user_id: UUID,
        user_service: UserService = Depends(get_user_service)
) -> User:
    """
    Страница пользователя
    """

    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='user not found')
    return User.from_model(user)
