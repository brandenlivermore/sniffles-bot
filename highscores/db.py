import sqlite3

sqlite_file = 'sniffles-bot-db.sqlite'
user_table_name = 'users'
id_col = 'id'
name_col = 'name'
connection = sqlite3.connect(sqlite_file)
c = connection.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS {table} (
                {id_col} TEXT NOT NULL, 
                {name_col} TEXT NOT NULL,
                CONSTRAINT id_unique UNIQUE ({id_col})
            );""".format(table=user_table_name, id_col=id_col, name_col=name_col))

c.execute(
    "CREATE INDEX IF NOT EXISTS user_id_indices ON {table} ({id_col})".format(table=user_table_name, id_col=id_col))

connection.commit()


def get_user_name(id):
    c = connection.cursor()
    result = None
    try:
        c.execute("""SELECT * 
                          FROM {table_name} 
                          WHERE {id_col}=?""".format(table_name=user_table_name, id_col=id_col), (id,))

        result = c.fetchone()
    except sqlite3.OperationalError as e:
        print(e)

    if result is None:
        return None

    return result[1]


def update_name(id, name):
    c = connection.cursor()
    try:
        c.execute("""UPDATE {table_name}
                        SET {name_col} = ?
                        WHERE {id_col} = ?""".format(table_name=user_table_name, name_col=name_col, id_col=id_col),
                  (name, id))
        connection.commit()
        return SetUserNameResult.Update
    except sqlite3.IntegrityError as e:
        print(e)
        return SetUserNameResult.Failure


class SetUserNameResult:
    FirstTime, Update, Failure, Same = range(4)


def set_user_name(id, name):
    c = connection.cursor()
    existing_name = get_user_name(id)

    if existing_name is not None:
        print(name)
        if existing_name == name:
            return SetUserNameResult.Same

        return update_name(id, name)

    result = SetUserNameResult.FirstTime
    try:
        global user_table_name, id_col, name_col
        c.execute("INSERT INTO {table_name} ({id_col}, {name_col}) VALUES (?, ?)".format(table_name=user_table_name,
                                                                                         id_col=id_col,
                                                                                         name_col=name_col), (id, name))
        connection.commit()
    except sqlite3.IntegrityError as e:
        print(e)
        result = SetUserNameResult.Failure

    return result
