from UserSession import UserSession


class UserService:

    def __init__(self):
        self._users = {}

    def get_user_session(self, user_id):
        if user_id not in self._users:
            self._users[user_id] = UserSession(0)
        return self._users[user_id]

    def set_user_session(self, user_id, state):
        session = self._users[user_id]
        session.state = state
