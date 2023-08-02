from datetime import date
from DB_connectors.config import host, user, password
import pymysql


class Database:
    def __init__(self, db_name):
        self.connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        self.connection.autocommit(True)

    def cbdt(self):
        with self.connection.cursor() as cursor:
            create = """CREATE TABLE IF NOT EXISTS users
                        (id INT PRIMARY KEY AUTO_INCREMENT,
                        telegram_id BIGINT UNIQUE NOT NULL ,
                        full_name TEXT,
                        username TEXT,
                        pay_end TEXT,
                        is_all_chats INT DEFAULT 1,
                        click_left INT NOT NULL DEFAULT 0
                        );"""
            cursor.execute(create)
            self.connection.commit()

        with self.connection.cursor() as cursor:
            create = """CREATE TABLE IF NOT EXISTS keywords
                    (id INT PRIMARY KEY AUTO_INCREMENT,
                    word VARCHAR(512) UNIQUE NOT NULL
                    );
                """
            cursor.execute(create)
            self.connection.commit()

        with self.connection.cursor() as cursor:
            create = """    CREATE TABLE IF NOT EXISTS unex_words
                    (id INT PRIMARY KEY AUTO_INCREMENT,
                    word VARCHAR(512) UNIQUE NOT NULL
                    );
                """
            cursor.execute(create)
            self.connection.commit()
        with self.connection.cursor() as cursor:
            create = """    CREATE TABLE IF NOT EXISTS chats
                    (id INT PRIMARY KEY AUTO_INCREMENT,
                    chat VARCHAR(512) UNIQUE NOT NULL,
                    chat_num INT,
                    chat_title TEXT);
                """
            cursor.execute(create)
            self.connection.commit()

        with self.connection.cursor() as cursor:
            create = """    CREATE TABLE IF NOT EXISTS users_chats
                    (id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL,
                    chat_id INT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(chat_id) REFERENCES chats(id)
                    );
                """
            cursor.execute(create)
            self.connection.commit()

        with self.connection.cursor() as cursor:
            create = """    CREATE TABLE IF NOT EXISTS users_keywords
                    (id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL,
                    keyword_id INT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(keyword_id) REFERENCES keywords(id)
                    );
                """
            cursor.execute(create)
            self.connection.commit()

        with self.connection.cursor() as cursor:
            create = """    CREATE TABLE IF NOT EXISTS users_unex_words
                    (id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL,
                    unex_word_id INT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(unex_word_id) REFERENCES unex_words(id)
                    )"""
            cursor.execute(create)
            self.connection.commit()

        with self.connection.cursor() as cursor:
            create = """    CREATE TABLE IF NOT EXISTS admins
                    (id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(512) UNIQUE NOT NULL
                    );
                    """
            cursor.execute(create)
            self.connection.commit()
            self.connection.close()

    def create_user(self, telegram_id, full_name: str, username: str, pay_end):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                'INSERT IGNORE INTO users (telegram_id, full_name, username, pay_end) VALUES(%s, %s, %s, %s)', (telegram_id, full_name, username, pay_end))
            self.connection.commit()
            self.connection.close()

    def click_use(self, telegram_id,):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                'UPDATE users SET click_left = click_left - 1 WHERE telegram_id =(%s)', (telegram_id,))
            self.connection.commit()
            self.connection.close()

    def click_add(self, amount: int, username,):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            sql = 'UPDATE users SET click_left = (%s) WHERE username = %s'
            cursor.execute(
                sql, (amount, username))
            self.connection.commit()
            self.connection.close()

    def click_left(self, telegram_id):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                'SELECT click_left FROM users WHERE telegram_id=(%s)', (telegram_id,))
            clicks = cursor.fetchone()[0]
            self.connection.close()
            return clicks

    def add_keyword(self, telegram_id: int, word: str):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''INSERT IGNORE INTO keywords(word) VALUES(%s)''', (word,))
            self.connection.commit()

        with self.connection.cursor() as cursor:
            cursor.execute(
                'INSERT IGNORE INTO users_keywords(user_id, keyword_id) VALUES ((SELECT id FROM users WHERE telegram_id=(%s)),(SELECT id FROM keywords WHERE word =(%s)))', (telegram_id, word))
            self.connection.commit()
            self.connection.close()
        # with self.connection.cursor() as cursor:
        #     cursor.execute(
        #         '''SELECT word
        #             FROM keywords
        #             WHERE id IN (SELECT keyword_id FROM users_keywords WHERE user_id =(SELECT id FROM users WHERE telegram_id=(%s))) ''', telegram_id)
        #     keywords = cursor.fetchall()
        #     return [i[0] for i in keywords]

    def add_unex_word(self, telegram_id: int, word: str):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                'INSERT IGNORE INTO unex_words(word) VALUES(%s)', (word,))
            self.connection.commit()

        with self.connection.cursor() as cursor:
            cursor.execute(
                'INSERT IGNORE INTO users_unex_words(user_id, unex_word_id) VALUES ((SELECT id FROM users WHERE telegram_id = (%s)),(SELECT id FROM unex_words WHERE word = (%s)))', (telegram_id, word))
            self.connection.commit()
            self.connection.close()
            # cursor.execute(
            #     '''SELECT word
            #         FROM unex_words
            #         WHERE id IN (SELECT unex_word_id FROM users_unex_words WHERE user_id =(SELECT id FROM users WHERE telegram_id=(%s))) ''', (telegram_id,))
            # keywords = cursor.fetchall()
            # return [i[0] for i in keywords]

    def add_chat(self, telegram_id: int, chat: str, chat_num: int = 1, chat_title=str):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''INSERT IGNORE INTO chats(chat,chat_num,chat_title) VALUES(%s,%s,%s)''', (chat, chat_num, chat_title))
            self.connection.commit()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM users WHERE telegram_id=(%s)", (telegram_id,))
            user_id = cursor.fetchone()[0]
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM chats WHERE chat=(%s)", (chat,))
            keyword_id = cursor.fetchone()[0]
        with self.connection.cursor() as cursor:
            cursor.execute(
                'INSERT IGNORE INTO users_chats(user_id, chat_id) VALUES (%s,%s)', (user_id, keyword_id))
            self.connection.commit()
        with self.connection.cursor() as cursor:
            keywords = cursor.execute(
                '''SELECT chat_title
                    FROM chats
                    WHERE id IN (SELECT chat_id FROM users_chats WHERE user_id =(SELECT id FROM users WHERE telegram_id=(%s))) ''', (telegram_id,))
            keywords = cursor.fetchall()
            self.connection.commit()
            self.connection.close()
            return [i[0] for i in keywords]

    def delete_all(self, telegram_id: int, table: str):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM users WHERE telegram_id = (%s)", (telegram_id,))
            user_id = cursor.fetchone()[0]
            cursor.execute(
                f'DELETE FROM {table} WHERE user_id = {user_id} ')
            self.connection.commit()
            self.connection.close()

    def all_words(self, telegram_id: int):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''SELECT word,id
                    FROM keywords
                    WHERE id IN (SELECT keyword_id FROM users_keywords WHERE user_id =(SELECT id FROM users WHERE telegram_id=(%s))) ''', (telegram_id,))
            keywords = cursor.fetchall()
            self.connection.close()
            return keywords

    def all_unex_words(self, telegram_id: int):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''SELECT word,id
                    FROM unex_words
                    WHERE id IN (SELECT unex_word_id FROM users_unex_words WHERE user_id =(SELECT id FROM users WHERE telegram_id=(%s))) ''', (telegram_id,))
            keywords = cursor.fetchall()
            self.connection.close()
            return keywords

    def chats_list(self):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''SELECT chat FROM chats''')
            keywords = cursor.fetchall()
            self.connection.close()
            return [i[0] for i in keywords]

    def all_user_chats(self, telegram_id: int):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''SELECT chat_title,chat_num
                    FROM chats
                    WHERE id IN (SELECT chat_id FROM users_chats WHERE user_id in (SELECT id FROM users WHERE telegram_id=(%s))) 
                    LIMIT 90;''', (telegram_id,))
            chats = cursor.fetchall()
            self.connection.close()
            return chats

    def remove_keyword(self, telegram_id: int, id):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                'DELETE FROM users_keywords WHERE user_id = (SELECT id FROM users WHERE telegram_id = (%s)) AND keyword_id = (SELECT id FROM keywords WHERE id = (%s))', (telegram_id, id))
            self.connection.commit()

            keywords = cursor.execute(
                '''SELECT word,id
                    FROM keywords
                    WHERE id IN (SELECT keyword_id FROM users_keywords WHERE user_id =(SELECT id FROM users WHERE telegram_id=(%s))) ''', (telegram_id,))
            keywords = cursor.fetchall()
            self.connection.close()
            return keywords

    def remove_keyword_from_table(self,  keyword: str):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM keywords WHERE word = (%s)", (keyword,))
            self.connection.commit()
            self.connection.close()

    def remove_unex_word(self, telegram_id: int, id: str):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM users WHERE telegram_id = (%s)", (telegram_id,))
            user_id = cursor.fetchone()
            cursor.execute(
                "SELECT id FROM unex_words WHERE id = (%s)", (id,))
            keyword_id = cursor.fetchone()
            cursor.execute(
                'DELETE FROM users_unex_words WHERE user_id =%s AND unex_word_id =%s', (user_id, keyword_id))
            self.connection.commit()
            cursor.execute(
                '''SELECT word,id
                    FROM unex_words
                    WHERE id IN (SELECT unex_word_id FROM users_unex_words WHERE user_id =(SELECT id FROM users WHERE telegram_id=(%s))) ''', (telegram_id,))
            keywords = cursor.fetchall()
            self.connection.close()
            return keywords

    def remove_chat(self, telegram_id: int, chat_num: str):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                'DELETE FROM users_chats WHERE user_id = (SELECT id FROM users WHERE telegram_id = (%s)) AND chat_id = (SELECT id FROM chats WHERE chat_num = (%s))', (telegram_id, chat_num))
            self.connection.commit()
            self.connection.close()

    def all_words_(self):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT word FROM keywords")
            words = cursor.fetchall()
            self.connection.close()
            return [i[0] for i in words]

    def all_unex_words_(self):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT word FROM unex_words")
            words = cursor.fetchall()
            self.connection.close()
            return [i[0] for i in words]

    def mailing_users(self, keywords, unex_words=tuple()):
        self.connection.ping()
        key = keywords
        unex = unex_words
        kids = ', '.join(['%s'] * len(key))
        uids = ', '.join(['%s'] * len(unex))
        with self.connection.cursor() as cursor:
            sql = f"SELECT telegram_id FROM users WHERE id IN (SELECT user_id FROM users_keywords WHERE keyword_id IN (SELECT id FROM keywords WHERE word IN ({kids})))"
            cursor.execute(sql, (key))
            key = cursor.fetchall()
            if unex != []:
                usql = f"SELECT telegram_id FROM users WHERE id IN (SELECT user_id FROM users_unex_words WHERE unex_word_id IN (SELECT id FROM unex_words WHERE word IN ({uids})))"
                cursor.execute(usql, (unex))
                unex = cursor.fetchall()
                users = [i for i in key if i not in unex]
                self.connection.close()
                return [i[0] for i in users]
            else:
                self.connection.close()
                return [i[0] for i in key]

    def add_chat_id(self, chat_id, chat):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                f'UPDATE chats SET chat_num={chat_id} WHERE chat="{chat}"')
            self.connection.commit()
            self.connection.close()

    def add_chat_id(self, telegram_id, status):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                f'UPDATE chats SET is_all_chats={str(status)} WHERE telegram_id={telegram_id}')
            self.connection.commit()
            self.connection.close()

    def get_status(self, telegram_id):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                'SELECT is_all_chats FROM users WHERE telegram_id=(%s)', (telegram_id,))
            is_subs = cursor.fetchone()[0]
            self.connection.close()
            return is_subs

    def set_status(self, telegram_id, status):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                'UPDATE users SET is_all_chats=(%s) WHERE telegram_id=(%s)', (status, telegram_id))
            self.connection.commit()
            self.connection.close()

    def pay(self, username: str, end_date):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                'UPDATE users SET pay_end=%s WHERE username=%s', (end_date, username))
            self.connection.commit()
            self.connection.close()

    def is_pay(self, telegram_id):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''SELECT pay_end FROM users WHERE telegram_id=(%s)''', (telegram_id,))
            pay_end = cursor.fetchone()[0]
            """По хорошему
            переписать на проверку на
            типах данных DATETIME"""
            self.connection.close()
        return str(pay_end) >= str(date.today())

    def add_admin(self, username):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''INSERT IGNORE INTO admins(username) VALUES (%s)''', (username,))
            self.connection.commit()
            self.connection.close()

    def is_admin(self, username):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT username FROM admins")
            res = cursor.fetchall()
            self.connection.close()
        return username in [i[0]for i in res]

    def get_chat_link(self, chat_id):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            chat = cursor.execute(
                "SELECT chat FROM chats WHERE chat_num=%s", chat_id)
            chat = cursor.fetchone()[0]
            self.connection.close()
            return chat

    def get_chat_id(self, title):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            chat = cursor.execute(
                "SELECT chat_num FROM chats WHERE chat_title=(%s)", title)
            chat = cursor.fetchone()[0]
            self.connection.close()
            return chat


if __name__ == "__main__":
    a = Database("TopLid")
    a.cbdt()
