import sqlite3

db_file = 'sniffles-bot-db.sqlite'
keywords_table = 'keywords'
id_col = 'id'
keyword_col = 'keyword'
itemid = 'itemid'

connection = sqlite3.connect(db_file)

c = connection.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS {table} (
                {id} TEXT NOT NULL, 
                {keyword} TEXT NOT NULL,
                {itemid} INT NOT NULL
            );""".format(table=keywords_table, id=id, keyword=keyword, itemid=itemid))

c.execute(
	"CREATE INDEX IF NOT EXISTS useridindex on {table} ({id_col})".format(table=keywords_table, id_col=id_col))
               
c.execute(
	"CREATE INDEX IF NOT EXISTS keywordindex on {table} ({keyword_col})".format(table=keywords_table, keyword_col=keyword_col))

connection.commit()

def item_id_for_keyword(userid, keyword):
	c = connection.cursor()
	result = None
	try:
		c.execute("""SELECT TOP 1 *
								FROM {table}
								WHERE {id_col}=? AND {keyword_col}=?""".format(table=keywords_table, id_col=id_col, keyword_col=keyword_col), (userid, keyword))
		
		result = int(c.fetch())
	except sqlite3.OperationalError as e:
		print(e)
	
	if result is None:
		return None
		
	return result													
