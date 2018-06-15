import sqlite3

db_file = 'sniffles-bot-db.sqlite'
keywords_table = 'keywords'
id_col = 'id'
keyword_col = 'keyword'
item_id_col = 'itemid'

connection = sqlite3.connect(db_file)

c = connection.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS {table} (
                {id_col} TEXT NOT NULL, 
                {name_col} TEXT NOT NULL,
                CONSTRAINT id_unique UNIQUE ({id_col})
            );""".format(table=keywords_table, id_col=id_col, name_col=item_id_col))



