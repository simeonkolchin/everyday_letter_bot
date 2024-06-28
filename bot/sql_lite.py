import sqlite3 as sl


async def db_connect():
    global con, cur

    con = sl.connect('data.db')
    cur = con.cursor()

    cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                   id BIGINT PRIMARY KEY,
                   photos TEXT
        );
            """)
    con.commit()


async def create_user(id, photos='7'):
    data = (id, photos)
    cur.execute("INSERT INTO users(id, photos) VALUES (?, ?);", data)
    con.commit()


async def update_user(id: int, photos: str, add: int):
    data = (photos + f' {add}', id)
    cur.execute("UPDATE users SET photos = ? WHERE id = ?;", data)
    con.commit()


async def get_user(id):
    user = cur.execute(f"SELECT * FROM users WHERE id = {id};").fetchall()
    return user


async def get_users():
    users = cur.execute(f"SELECT id FROM users").fetchall()
    return users
