import sqlite3

db_file = 'sniffles-bot-db.sqlite'
keywords_table = 'keywords'
id_col = 'id'
keyword_col = 'keyword'
itemid_col = 'itemid'

connection = sqlite3.connect(db_file)

c = connection.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS {table} (
                {id_col} TEXT NOT NULL, 
                {keyword_col} TEXT NOT NULL,
                {itemid_col} INT NOT NULL
            );""".format(table=keywords_table, id_col=id_col, keyword_col=keyword_col, itemid_col=itemid_col))

c.execute(
    "CREATE INDEX IF NOT EXISTS useridindex on {table} ({id_col})".format(table=keywords_table, id_col=id_col))

c.execute(
    "CREATE INDEX IF NOT EXISTS keywordindex on {table} ({keyword_col})".format(table=keywords_table,
                                                                                keyword_col=keyword_col))

connection.commit()

def item_id_for_keyword(userid, keyword):
    c = connection.cursor()
    result = None
    try:
        c.execute("""SELECT {itemid_col}
                                FROM {table}
                                WHERE {id_col}=? AND {keyword_col}=?
                                LIMIT 1""".format(itemid_col=itemid_col,
                                                  table=keywords_table,
                                                  id_col=id_col,
                                                  keyword_col=keyword_col),
                  (userid, keyword))
        fetch = c.fetchone()
        if fetch is not None:
            result = fetch[0]
    except sqlite3.OperationalError as e:
        print(e)

    if result is None:
        return None

    return result


def set_keyword_for_item(userid, keyword, itemid):
    c = connection.cursor()
    exists = item_id_for_keyword(userid, keyword) == itemid

    if exists:
        return

    try:
        query = "INSERT INTO {table} ({id_col}, {keyword_col}, {itemid_col}) VALUES (?, ?, ?)".format(
            table=keywords_table,
            id_col=id_col,
            keyword_col=keyword_col,
            itemid_col=itemid_col)
        c.execute(query, (userid, keyword, itemid))
        connection.commit()
    except sqlite3.IntegrityError as e:
        print(e)


set_keyword_for_item("guidwow", "keyword", 69)

print(item_id_for_keyword("guidwow", "keyword"))
print(item_id_for_keyword("guidwow", "fjklsd"))
