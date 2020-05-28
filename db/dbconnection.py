import sqlite3
import uuid
from db.itemgroup import ItemGroup
import db

db_file = 'sniffles-bot-db.sqlite'
# Grand Exchange
keywords_table = 'keywordsgroupusers'
userid_col = 'userid'
keyword_col = 'keyword'
groupid_col = 'groupid'
groupname_col = 'name'

group_table = 'groups'

group_item_table = 'group_items'
itemid_col = 'itemid'

# Messages for maximum Chris trolling
messages_table = 'messages'
message_id_col = 'message_id'
member_id_col = 'member_id'
content_col = 'content'
url_col = 'url'
date_col = 'date'

connection = sqlite3.connect(db_file)
connection.execute('pragma foreign_keys=ON')
c = connection.cursor()

# Messages table
c.execute("""CREATE TABLE IF NOT EXISTS {table} (
                {message_id_col} INT NOT NULL, 
                {member_id_col} INT NOT NULL,
                {content_col} TEXT NOT NULL,
                {url_col} TEXT NOT NULL,
                {date_col} INT NOT NULL
            );""".format(table=messages_table,
                         message_id_col=message_id_col,
                         member_id_col=member_id_col,
                         content_col=content_col,
                         url_col=url_col,
                         date_col=date_col))

# User + keyword to group
c.execute("""CREATE TABLE IF NOT EXISTS {table} (
                {userid_col} TEXT NOT NULL, 
                {keyword_col} TEXT NOT NULL,
                {groupid_col} TEXT NOT NULL,
                FOREIGN KEY ({groupid_col}) REFERENCES {group_table}({groupid_col})
            );""".format(table=keywords_table,
                         userid_col=userid_col,
                         keyword_col=keyword_col,
                         groupid_col=groupid_col,
                         group_table=group_table))

c.execute("""CREATE UNIQUE INDEX IF NOT EXISTS keyword_index 
             ON {table} ({userid_col}, {keyword_col});""".format(table=keywords_table,
                                                                 userid_col=userid_col,
                                                                 keyword_col=keyword_col))

# Group to group name
c.execute("""CREATE TABLE IF NOT EXISTS {table} (
                {groupid_col} TEXT NOT NULL,
                {groupname_col} TEXT NULL,
                CONSTRAINT id_unique UNIQUE ({groupid_col})
            );""".format(table=group_table,
                         groupname_col=groupname_col,
                         groupid_col=groupid_col))

c.execute("""CREATE INDEX IF NOT EXISTS group_id_index
             ON {table} ({groupid_col});""".format(table=group_table,
                                                   groupid_col=groupid_col))

# Group to item ids
c.execute("""CREATE TABLE IF NOT EXISTS {table} (
             {groupid_col} TEXT NOT NULL,
             {itemid_col} INT NOT NULL,
             CONSTRAINT group_item_unique UNIQUE ({groupid_col}, {itemid_col}),
             FOREIGN KEY ({groupid_col}) REFERENCES {group_table}({groupid_col})
          );""".format(table=group_item_table,
                       groupid_col=groupid_col,
                       itemid_col=itemid_col,
                       group_table=group_table))

c.execute("""CREATE INDEX IF NOT EXISTS item_index
             ON {table} ({groupid_col});""".format(table=group_item_table,
                                                   groupid_col=groupid_col))

connection.commit()


def remove_item_from_keyword(user_id, keyword, item_id):
    group_id, group = item_group_for_keyword_with_id(user_id, keyword)

    if group is None:
        return False

    count = len(group.items)

    if item_id not in group.items:
        return False

    if count is 1:
        remove_keyword(user_id, keyword)
    else:
        remove_item_from_group(group_id, item_id)

    return True


def remove_keyword(user_id, keyword):
    group_id = get_group_id(user_id, keyword)

    if group_id is None:
        return False
    else:
        remove_group(group_id)
        return True


def set_keyword_for_item(user_id, keyword, item_id):
    group_id = get_or_create_user_group(user_id, keyword)

    add_item_to_group(group_id, item_id)

    return item_group_for_keyword(user_id, keyword)


def set_user_group_name(user_id, keyword, name):
    group_id = get_group_id(user_id, keyword)

    if group_id is None:
        return False
    else:
        set_group_name(group_id, name)
        return True


def item_group_for_keyword(user_id, keyword):
    return item_group_for_keyword_with_id(user_id, keyword)[1]


def item_group_for_keyword_with_id(user_id, keyword):
    c = connection.cursor()
    c.execute("""SELECT {groupname_col}, {itemid_col}, {keywords_table}.{groupid_col}
                 FROM {group_item_table}
                 INNER JOIN {group_table}
                    ON {group_table}.{groupid_col} = {group_item_table}.{groupid_col}
                 INNER JOIN {keywords_table}
                    ON {keywords_table}.{groupid_col} = {group_table}.{groupid_col}
                 WHERE {userid_col} = ? AND {keyword_col} = ?""".format(groupname_col=groupname_col,
                                                                        itemid_col=itemid_col,
                                                                        group_item_table=group_item_table,
                                                                        group_table=group_table,
                                                                        groupid_col=groupid_col,
                                                                        keywords_table=keywords_table,
                                                                        userid_col=userid_col,
                                                                        keyword_col=keyword_col), (user_id, keyword))

    results = c.fetchall()

    if len(results) is 0:
        return None, None

    group_name = results[0][0]

    items = [item[1] for item in results]

    return results[0][2], ItemGroup(keyword, group_name, items)


def get_or_create_user_group(user_id, keyword):
    return get_group_id(user_id, keyword) or create_user_group(user_id, keyword)


def get_group_id(user_id, keyword):
    c = connection.cursor()

    c.execute("""SELECT {groupid_col}
                 FROM {table}
                 WHERE {userid_col} = ? AND {keyword_col} = ?
                 LIMIT 1;""".format(groupid_col=groupid_col,
                                    table=keywords_table,
                                    userid_col=userid_col,
                                    keyword_col=keyword_col), (user_id, keyword))

    fetch = c.fetchone()

    if fetch is None:
        return None
    else:
        return fetch[0]


def create_user_group(user_id, keyword):
    guid = create_group()

    c = connection.cursor()

    c.execute("""INSERT INTO {table}
                 ({userid_col}, {keyword_col}, {groupid_col}) VALUES (?, ?, ?);""".format(table=keywords_table,
                                                                                          userid_col=userid_col,
                                                                                          keyword_col=keyword_col,
                                                                                          groupid_col=groupid_col),
              (user_id, keyword, guid))

    connection.commit()

    return guid


def create_group():
    c = connection.cursor()

    guid = str(uuid.uuid4())

    c.execute("""INSERT INTO {table} 
                 ({groupid_col}) VALUES (?);""".format(table=group_table,
                                                       groupid_col=groupid_col), (guid,))

    connection.commit()

    return guid


def set_group_name(group_id, name):
    c = connection.cursor()

    c.execute("""UPDATE {table}
                 SET {groupname_col} = ?
                 WHERE {groupid_col} = ?;""".format(table=group_table,
                                                    groupname_col=groupname_col,
                                                    groupid_col=groupid_col), (name, group_id))

    connection.commit()


def add_item_to_group(group_id, item_id):
    c = connection.cursor()

    try:
        c.execute("""INSERT INTO {table} 
                     ({groupid_col}, {itemid_col}) VALUES (?, ?);""".format(table=group_item_table,
                                                                            groupid_col=groupid_col,
                                                                            itemid_col=itemid_col), (group_id, item_id))
    except sqlite3.IntegrityError as e:
        return

    connection.commit()


def remove_item_from_group(group_id, item_id):
    c = connection.cursor()

    c.execute("""DELETE FROM {table}
                 WHERE {groupid_col} = ? AND {itemid_col} = ?;""".format(table=group_item_table,
                                                                         groupid_col=groupid_col,
                                                                         itemid_col=itemid_col), (group_id, item_id))

    connection.commit()


def remove_group(group_id):
    c = connection.cursor()

    c.execute("""DELETE FROM {table}
                 WHERE {groupid_col} = ?;""".format(table=keywords_table,
                                                    groupid_col=groupid_col), (group_id,))

    c.execute("""DELETE FROM {table}
                 WHERE {groupid_col} = ?;""".format(table=group_item_table,
                                                    groupid_col=groupid_col), (group_id,))

    c.execute("""DELETE FROM {table}
                 WHERE {groupid_col} = ?;""".format(table=group_table,
                                                    groupid_col=groupid_col), (group_id,))

    connection.commit()


def insert_messages(messages):
    delete_messages()

    c = connection.cursor()

    for message_entry in messages:
        c.execute("""INSERT INTO {table}
                     ({message_id_col}, {member_id_col}, {content_col}, {url_col}, {date_col}) VALUES (?, ?, ?, ?, ?);""".format(table=messages_table,
                                                                                                                                               message_id_col=message_id_col,
                                                                                                                                               member_id_col=member_id_col,
                                                                                                                                               content_col=content_col,
                                                                                                                                               url_col=url_col,
                                                                                                                                               date_col=date_col),
                  (message_entry.message_id, message_entry.member_id, message_entry.content, message_entry.url, message_entry.date))

    connection.commit()

def delete_messages():
    c = connection.cursor()

    c.execute("""DELETE FROM {table}""".format(table=messages_table))
    connection.commit()

def messages_for_member(member_id):
    c = connection.cursor()
    c.execute("""SELECT {message_id_col}, {member_id_col}, {content_col}, {url_col}, {date_col}
                 FROM {table}
                 WHERE {member_id_col} = ?""".format(table=messages_table,
                                                     message_id_col=message_id_col,
                                                     member_id_col=member_id_col,
                                                     content_col=content_col,
                                                     url_col=url_col,
                                                     date_col=date_col), (member_id,))

    results = c.fetchall()

    if len(results) is 0:
        return None

    return list(map(message_result_to_message_entry, results))

def message_result_to_message_entry(result):
    return db.MessageEntry(result[0], result[1], result[2], result[3], result[4])