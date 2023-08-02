import sqlite3
from datetime import date


class Database:
    def __init__(self, db_file) -> None:

        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def cbdt(self):
        with self.connection:
            create = """ CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL UNIQUE ON CONFLICT IGNORE,
                    full_name TEXT,
                    username TEXT,
                    pay_end TEXT,
                    is_all_chats INTEGER DEFAULT 1
                    );

                    CREATE TABLE IF NOT EXISTS keywords
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL UNIQUE ON CONFLICT IGNORE
                    );

                    CREATE TABLE IF NOT EXISTS unex_words
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL UNIQUE ON CONFLICT IGNORE
                    );

                    CREATE TABLE IF NOT EXISTS chats
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat TEXT NOT NULL UNIQUE ON CONFLICT IGNORE,
                    chat_num INTEGER,
                    chat_title TEXT);

                    CREATE TABLE IF NOT EXISTS users_chats
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    chat_id INTEGER NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                    FOREIGN KEY(chat_id) REFERENCES chats(id)
                    );

                    CREATE TABLE IF NOT EXISTS users_keywords
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    keyword_id INTEGER NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                    FOREIGN KEY(keyword_id) REFERENCES keywords(id)
                    );

                    CREATE TABLE IF NOT EXISTS users_unex_words
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    unex_word_id INTEGER NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                    FOREIGN KEY(unex_word_id) REFERENCES unex_words(id)
                    );

                    CREATE TABLE IF NOT EXISTS admins
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE ON CONFLICT IGNORE
                    );
                    """
            self.cursor.executescript(create)

    def create_user(self, telegram_id: int, full_name: str, username: str, pay_end):
        with self.connection:
            self.cursor.execute(
                'INSERT INTO users(telegram_id, full_name, username,pay_end )VALUES(?,?,?,?)', (telegram_id, full_name, username, pay_end))

    def add_keyword(self, telegram_id: int, word: str):
        with self.connection:
            self.cursor.execute(
                '''INSERT INTO keywords(word) VALUES(?)''', (word,))
        with self.connection:
            user_id = self.cursor.execute(
                "SELECT id FROM users WHERE telegram_id == (?)", (telegram_id,)).fetchone()[0]
        with self.connection:
            keyword_id = self.cursor.execute(
                "SELECT id FROM keywords WHERE word == (?)", (word,)).fetchone()[0]
        with self.connection:
            self.cursor.execute(
                'INSERT INTO users_keywords(user_id, keyword_id) VALUES (?,?)', (user_id, keyword_id))
        with self.connection:
            keywords = self.cursor.execute(
                '''SELECT word
                FROM keywords
                WHERE id IN (SELECT keyword_id FROM users_keywords WHERE user_id ==(SELECT id FROM users WHERE telegram_id==(?))) ''', (telegram_id,)).fetchall()
        return [i[0] for i in keywords]

    def add_unex_word(self, telegram_id: int, word: str):
        with self.connection:
            self.cursor.execute(
                '''INSERT INTO unex_words(word) VALUES(?)''', (word,))
        with self.connection:
            user_id = self.cursor.execute(
                "SELECT id FROM users WHERE telegram_id == (?)", (telegram_id,)).fetchone()[0]
        with self.connection:
            keyword_id = self.cursor.execute(
                "SELECT id FROM unex_words WHERE word == (?)", (word,)).fetchone()[0]
        with self.connection:
            self.cursor.execute(
                'INSERT INTO users_unex_words(user_id, unex_word_id) VALUES (?,?)', (user_id, keyword_id))

        with self.connection:
            keywords = self.cursor.execute(
                '''SELECT word
                FROM unex_words
                WHERE id IN (SELECT unex_word_id FROM users_unex_words WHERE user_id ==(SELECT id FROM users WHERE telegram_id==(?))) ''', (telegram_id,)).fetchall()
            return [i[0] for i in keywords]

    def add_chat(self, telegram_id: int, chat: str, chat_num: int = 1, chat_title=str):

        with self.connection:
            print(chat, chat_num)
            self.cursor.execute(
                '''INSERT INTO chats(chat,chat_num,chat_title) VALUES(?,?,?)''', (chat, chat_num, chat_title))
        with self.connection:
            user_id = self.cursor.execute(
                "SELECT id FROM users WHERE telegram_id=(?)", (telegram_id,)).fetchone()[0]
        with self.connection:
            keyword_id = self.cursor.execute(
                "SELECT id FROM chats WHERE chat=(?)", (chat,)).fetchone()[0]
        with self.connection:
            self.cursor.execute(
                'INSERT INTO users_chats(user_id, chat_id) VALUES (?,?)', (user_id, keyword_id))

        with self.connection:
            keywords = self.cursor.execute(
                '''SELECT chat_title
                FROM chats
                WHERE id IN (SELECT chat_id FROM users_chats WHERE user_id ==(SELECT id FROM users WHERE telegram_id==(?))) ''', (telegram_id,)).fetchall()
            return [i[0] for i in keywords]

    def delete_all(self, telegram_id: int, table: str):
        with self.connection:
            user_id = self.cursor.execute(
                "SELECT id FROM users WHERE telegram_id == (?)", (telegram_id,)).fetchone()[0]
        with self.connection:
            self.cursor.execute(
                f'DELETE FROM {table} WHERE user_id == {user_id} ')

    def all_words(self, telegram_id: int):
        with self.connection:
            keywords = self.cursor.execute(
                '''SELECT word
                FROM keywords
                WHERE id IN (SELECT keyword_id FROM users_keywords WHERE user_id ==(SELECT id FROM users WHERE telegram_id==(?))) ''', (telegram_id,)).fetchall()
        return [i[0] for i in keywords]

    def all_unex_words(self, telegram_id: int):
        with self.connection:
            keywords = self.cursor.execute(
                '''SELECT word
                FROM unex_words
                WHERE id IN (SELECT unex_word_id FROM users_unex_words WHERE user_id ==(SELECT id FROM users WHERE telegram_id==(?))) ''', (telegram_id,)).fetchall()
        return [i[0] for i in keywords]

    def all_chats(self, telegram_id: int):
        with self.connection:
            keywords = self.cursor.execute(
                '''SELECT chat_num
                FROM chats
                WHERE id IN (SELECT chat_id FROM users_chats WHERE user_id ==(SELECT id FROM users WHERE telegram_id==(?))) ''', (telegram_id,)).fetchall()
        return [i[0] for i in keywords]

    def all_user_chats(self, telegram_id: int):
        with self.connection:
            keywords = self.cursor.execute(
                '''SELECT chat_title
                FROM chats
                WHERE id IN (SELECT chat_id FROM users_chats WHERE user_id ==(SELECT id FROM users WHERE telegram_id==(?))) ''', (telegram_id,)).fetchall()
        return [i[0] for i in keywords]

    def remove_keyword(self, telegram_id: int, keyword: str):
        with self.connection:
            user_id = self.cursor.execute(
                "SELECT id FROM users WHERE telegram_id == (?)", (telegram_id,)).fetchone()[0]
        with self.connection:
            keyword_id = self.cursor.execute(
                "SELECT id FROM keywords WHERE word == (?)", (keyword,)).fetchone()[0]
        with self.connection:
            self.cursor.execute(
                f'DELETE FROM users_keywords WHERE user_id == {user_id} AND keyword_id =={keyword_id}')
        with self.connection:
            keywords = self.cursor.execute(
                '''SELECT word
                FROM keywords
                WHERE id IN (SELECT keyword_id FROM users_keywords WHERE user_id ==(SELECT id FROM users WHERE telegram_id==(?))) ''', (telegram_id,)).fetchall()
        return [i[0] for i in keywords]

    def remove_keyword_(self,  keyword: str):
        with self.connection:
            self.cursor.execute(
                "DELETE FROM keywords WHERE word == (?)", (keyword,))

    def remove_unex_word(self, telegram_id: int, unex_word: str):
        with self.connection:
            user_id = self.cursor.execute(
                "SELECT id FROM users WHERE telegram_id == (?)", (telegram_id,)).fetchone()[0]
        with self.connection:
            keyword_id = self.cursor.execute(
                "SELECT id FROM unex_words WHERE word == (?)", (unex_word,)).fetchone()[0]
        with self.connection:
            self.cursor.execute(
                f'DELETE FROM users_unex_words WHERE user_id == {user_id} AND unex_word_id =={keyword_id}')
        with self.connection:
            keywords = self.cursor.execute(
                '''SELECT word
                FROM unex_words
                WHERE id IN (SELECT unex_word_id FROM users_unex_words WHERE user_id ==(SELECT id FROM users WHERE telegram_id==(?))) ''', (telegram_id,)).fetchall()
        return [i[0] for i in keywords]

    def remove_chat(self, telegram_id: int, chat: str):
        with self.connection:
            user_id = self.cursor.execute(
                "SELECT id FROM users WHERE telegram_id == (?)", (telegram_id,)).fetchone()[0]
        with self.connection:
            chat_id = self.cursor.execute(
                "SELECT id FROM chats WHERE chat == (?)", (chat,)).fetchone()[0]
        with self.connection:
            self.cursor.execute(
                f'DELETE FROM users_chats WHERE user_id == {user_id} AND chat_id =={chat_id}')
        with self.connection:
            keywords = self.cursor.execute(
                '''SELECT chat
                    FROM chats
                    WHERE id IN (SELECT chat_id FROM users_chats WHERE user_id ==(SELECT id FROM users WHERE telegram_id==(?))) ''', (telegram_id,)).fetchall()
        return [i[0] for i in keywords]

    def all_words_(self):
        with self.connection:
            words = self.cursor.execute("SELECT word FROM keywords").fetchall()
        return [i[0] for i in words]

    def all_unex_words_(self):
        with self.connection:
            words = self.cursor.execute(
                "SELECT word FROM unex_words").fetchall()
        return [i[0] for i in words]

    def mailing_users(self, keywords, unex_words=tuple()):
        key = str(keywords)[1:-1]
        unex = str(unex_words)[1:-1]
        users = self.cursor.execute(
            f"""SELECT telegram_id
                    FROM users
                    WHERE id IN
                    (SELECT user_id FROM users_keywords WHERE keyword_id
                    IN
                    (SELECT id FROM keywords WHERE word IN """ + """(""" + key + """)))
                    AND id NOT IN
                    (SELECT user_id FROM users_unex_words WHERE unex_word_id
                    IN
                    (SELECT id FROM unex_words WHERE word IN """ + """(""" + unex + """)))
                    ;""").fetchall()

        return [i[0] for i in users]

    def add_chat_id(self, chat_id, chat):
        with self.connection:
            self.cursor.execute(
                f'UPDATE chats SET chat_num={chat_id} WHERE chat="{chat}"')

    def add_chat_id(self, telegram_id, status):
        with self.connection:
            self.cursor.execute(
                f'UPDATE chats SET is_all_chats={str(status)} WHERE telegram_id={telegram_id}')

    def get_status(self, telegram_id):
        with self.connection:
            is_subs = self.cursor.execute(
                f'SELECT is_all_chats FROM users WHERE telegram_id={telegram_id}').fetchone()
        return is_subs[0]

    def set_status(self, telegram_id, status):
        with self.connection:
            self.cursor.execute(
                f'UPDATE users SET is_all_chats={status} WHERE telegram_id={telegram_id}')

    def pay(self, username: str, end_date):
        with self.connection:
            self.cursor.execute(
                f'''UPDATE users SET pay_end='{end_date}' WHERE username="{username}"''')

    def is_pay(self, telegram_id):
        with self.connection:
            pay_end = self.cursor.execute(
                f'''SELECT pay_end FROM users WHERE telegram_id="{telegram_id}"''').fetchone()[0]
        return pay_end >= str(date.today())

    def add_admin(self, username):
        with self.connection:
            self.cursor.execute(
                f'''INSERT INTO admins(username) VALUES ("{username}")''')

    def is_admin(self, username, telegram_id):
        with self.connection:
            admins = self.cursor.execute(
                f'''SELECT username FROM admins WHERE username="{username}"''').fetchall()
        return username in [admin[0] for admin in admins]

    def get_chat_link(self, chat_id):
        print(chat_id)
        with self.connection:
            chat = self.cursor.execute(
                f"SELECT chat FROM chats WHERE chat_num='{chat_id}'").fetchone()
        return chat[0]


if __name__ == "__main__":
    a = Database("TopLid")
    a.cbdt()
