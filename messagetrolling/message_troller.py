from db import dbconnection, MessageEntry
from datetime import timezone
import random

chris_id = 319299307960270858

class MessageTroller(object):
    def store_messages(self, messages):
        message_entries = list(map(message_to_message_entry, messages))

        dbconnection.insert_messages(message_entries)

    def random_chris_message(self, query):
        message_entries = dbconnection.messages_for_member(chris_id, query)

        if message_entries is None:
            return None

        print(len(message_entries))

        return random.choice(message_entries)

def message_to_message_entry(message):
    timestamp = message.created_at.replace(tzinfo=timezone.utc).timestamp()
    return MessageEntry(message.id, message.author.id, message.content, message.jump_url, timestamp)


