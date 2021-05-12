from common.models import Recommendations
from common.errors import UserNotFound, InvalidUUID
from common.utils import is_valid_uuid


def get_personal_recommendations(session, user_id):
    if not is_valid_uuid(user_id):
        raise InvalidUUID(user_id)
    recommendations = (
        session.query(Recommendations)
        .filter(Recommendations.userId == user_id)
        .one_or_none()
    )
    if not recommendations:
        raise UserNotFound(user_id)

    recommendations_dict = dict(recommendations.recommendations)
    return list(recommendations_dict['must_watch'])
