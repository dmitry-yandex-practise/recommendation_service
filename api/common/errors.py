class UserNotFound(Exception):
    def __init__(self, user_id):
        self.message = f'User {user_id} not found'


class InvalidUUID(Exception):
    def __init__(self, id_):
        self.message = f'Value "{id_}" is not a valid UUID4'
