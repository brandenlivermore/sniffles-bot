class MessageEntry(object):
    def __init__(self, message_id, member_id, content, url, date):
        self.message_id = message_id
        self.member_id = member_id
        self.content = content
        self.url = url
        self.date = date