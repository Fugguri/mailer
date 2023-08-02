from datetime import date
from .config import host, user, password,port
import pymysql


class Database:
    def __init__(self, db_name):
        self.connection = pymysql.connect(
            host=host,
            user=user,
            port=port,
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
                        clients INT
                        );"""
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

        with self.connection.cursor() as cursor:
            create = """    CREATE TABLE IF NOT EXISTS clients
                    (id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT,
                    api_id BIGINT,
                    api_hash TEXT,
                    phone TEXT,
                    message TEXT,
                    is_active BOOL DEFAULT false,
                    mailing_interval INT DEFAULT 1,
                    is_working BOOL DEFAULT false,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                    );
                    """
            cursor.execute(create)
            self.connection.commit()

        with self.connection.cursor() as cursor:
            create = """    CREATE TABLE IF NOT EXISTS chats
                    (id INT PRIMARY KEY AUTO_INCREMENT,
                    link TEXT,
                    name BIGINT,
                    chat_id BIGINT,
                    client_id INT,
                    FOREIGN KEY(client_id) REFERENCES clients(id)
                    );
                    """
            cursor.execute(create)
            self.connection.commit()

    def create_user(self, telegram_id, full_name: str, username: str, pay_end):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                'INSERT IGNORE INTO users (telegram_id, full_name, username, pay_end) VALUES(%s, %s, %s, %s)', (telegram_id, full_name, username, pay_end))
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
            """переписать на проверку на
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

    def create_client(self, telegram_id, api_id, api_hash, phone_number):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT IGNORE INTO clients(api_id, api_hash, phone,user_id) VALUES(%s,%s,%s, (SELECT id FROM users WHERE telegram_id=%s)) ",
                           (api_id, api_hash, phone_number, telegram_id))
            res = cursor.fetchall()
        self.connection.close()
        return res in [i[0]for i in res]

    def all_user_clients(self, telegram_id):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT phone FROM clients WHERE user_id=(SELECT id FROM users WHERE telegram_id=(%s))", (telegram_id,))
            res = cursor.fetchall()
        self.connection.close()
        return [i[0]for i in res]

    def all_user_clients_for_mailing(self, telegram_id):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM clients WHERE user_id=(SELECT id FROM users WHERE telegram_id=(%s))", (telegram_id,))
            res = cursor.fetchall()
        self.connection.close()
        return res

    def activate_client(self, phone):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE clients SET is_active=1 WHERE phone=%s", (phone))
            res = cursor.fetchall()
            self.connection.close()

    def deactivate_client(self, phone):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE clients SET is_active=0 WHERE phone=%s", (phone))
            res = cursor.fetchall()
            self.connection.close()

    def client_on(self, phone):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE clients SET is_working=1 WHERE phone=%s", (phone))
            res = cursor.fetchall()
            self.connection.close()

    def client_off(self, phone):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE clients SET is_working=0 WHERE phone=%s", (phone))
            res = cursor.fetchall()
            self.connection.close()

    def edit_mail_text(self, phone, message):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("UPDATE clients SET message=%s WHERE phone=%s ",
                           (message, phone))
        self.connection.close()

    def edit_mailing_interval(self, phone, interval):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("UPDATE clients SET mailing_interval=%s WHERE phone=%s ",
                           (interval, phone))
        self.connection.close()

    def get_data_for_client(self, phone):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM clients c RIGHT JOIN users u ON c.user_id=u.id WHERE phone=(%s)", (phone))
            res = cursor.fetchall()
        self.connection.close()
        return res[0]

    def mailing_chats(self, client_id):

        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM chats WHERE client_id=%s", (client_id))
            res = cursor.fetchall()
        self.connection.close()
        return res

    def add_chat(self, link, name, chat_id, client_id):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT IGNORE INTO chats(link, name, chat_id, client_id) VALUES(%s, %s, %s, %s) ", (link, name, chat_id, client_id))
            res = cursor.fetchall()
        self.connection.close()
        return res

    def client_chats(self, client_id):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM chats WHERE id=%s", (client_id))
            res = cursor.fetchall()
        self.connection.close()
        return res

    def get_chats_list(self, phone,user_id):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM chats WHERE client_id=(SELECT id FROM clients WHERE user_id=(SELECT id FROM users WHERE telegram_id=%s ) and phone=%s)", (user_id,phone))
            res = cursor.fetchall()
        self.connection.close()
        return res

    def get_active_clients(self):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM clients WHERE is_active=1")
            res = cursor.fetchall()
        self.connection.close()
        return res


if __name__ == "__main__":
    a = Database("swm")
    a.cbdt()
