import json

class notification_class():
    def __init__(self, id, user_id, notification, last_sent):
        self.id = id
        self.user_id = user_id
        self.notification = notification
        self.last_sent = last_sent
    
    def json(self):
        n = json.loads(self.notification)
        return n


class user_class():
    def __init__(self, id, username, email, phone):
        self.id = id
        self.username = username
        self.email = email
        self.phone = phone

class empty_class():
    pass
