import json


class UserInfo:
    def __init__(self, user_id, username, first_name, last_name, phone, is_bot):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.is_bot = is_bot

    def serialize(self):
        return json.dumps(self.__dict__, indent=2, ensure_ascii=False)
