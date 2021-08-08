class Player:

    def __init__(self, user_id, user_name, user_nick=None):
        self.user_id = user_id
        self.user_name = user_name
        self.user_nick = user_nick

    def __str__(self):
        return self.user_name
