import psycopg2
import configparser
import os


class TGBotDB:
    def __init__(self):
        config = configparser.ConfigParser()
        config_file_path = os.getenv('CONFIG_FILE_PATH', 'config.ini')
        with open(config_file_path) as config_file:
            config.read_file(config_file)
        self.dbname = config['dbaccess']['dbname']
        self.user = config['dbaccess']['user']
        self.password = config['dbaccess']['password']
        self.host = config['dbaccess']['host']
        self.port = config['dbaccess']['port']

    # Подключение к базе
    def connecting(self):
        return psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )

    # Создание таблиц
    def create_db(self):
        conn = psycopg2.connect(
            dbname='postgres',
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        cur = conn.cursor()
        conn.autocommit = True
        cur.execute("CREATE DATABASE tg_bot_db")
        conn.close()

    def create_tables(self):
        conn = self.connecting()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                cid BIGINT UNIQUE
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id SERIAL PRIMARY KEY,
                en_word VARCHAR(255) UNIQUE,
                ru_translate VARCHAR(255)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_words (
                id SERIAL PRIMARY KEY,
                cid BIGINT,
                en_word VARCHAR(255),
                ru_translate VARCHAR(255),
                FOREIGN KEY (cid) REFERENCES users(cid)
            )
        """)
        conn.commit()
        conn.close()

    # Удаление всех таблиц
    def delete_tables(self):
        conn = self.connecting()
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS user_words")
        cur.execute("DROP TABLE IF EXISTS words")
        cur.execute("DROP TABLE IF EXISTS users")
        conn.commit()
        conn.close()

    # Список пользователей
    def user_list(self):
        conn = self.connecting()
        cur = conn.cursor()
        cur.execute("SELECT cid FROM users")
        users = cur.fetchall()
        conn.close()
        users = [user[0] for user in users]
        return users

    # Добавление слов в базу данных
    def add_word(self, en_word, ru_translate):
        conn = self.connecting()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO words (en_word, ru_translate) "
            "VALUES (%s, %s) ON CONFLICT (en_word) DO NOTHING",
            (en_word, ru_translate))
        conn.commit()
        conn.close()

    # Добавление слова пользователя в базу данных
    def add_user_word(self, cid, text):
        en_word = text.split()[0]
        ru_translate = text.split()[1]
        conn = self.connecting()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO user_words (cid, en_word, ru_translate) "
            "VALUES (%s, %s, %s)",
            (cid, en_word, ru_translate))
        conn.commit()
        conn.close()

    # Добавление пользователя
    def add_user(self, cid):
        conn = self.connecting()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (cid) VALUES (%s)", (cid,))
        conn.commit()
        conn.close()

    # Получение слов из базы данных
    def get_words(self):
        conn = self.connecting()
        cur = conn.cursor()
        cur.execute("SELECT en_word, ru_translate FROM words")
        all_words = cur.fetchall()
        conn.close()
        return all_words

    # Получение всех слов пользователя из его базы данных
    def get_user_words(self, cid):
        conn = self.connecting()
        cur = conn.cursor()
        cur.execute("SELECT en_word, ru_translate "
                    "FROM user_words WHERE cid = %s", (cid,))
        all_user_words = cur.fetchall()
        conn.close()
        return all_user_words

    # Удаление слова пользователя из его базы данных
    def delete_user_word(self, cid, text):
        en_word = text.split()[0]
        conn = self.connecting()
        cur = conn.cursor()
        cur.execute("DELETE FROM user_words "
                    "WHERE cid = %s AND (en_word = %s OR ru_translate = %s)",
                    (cid, en_word, en_word))
        affected_rows = cur.rowcount
        conn.commit()
        conn.close()
        return affected_rows > 0

    # Создание тестовых слов в базе данных
    def add_test_data(self):
        test_words = [
            ('midge', 'мошка'),
            ('landscape', 'пейзаж'),
            ('sturgeon', 'осётр'),
            ('tadpole', 'головастик'),
            ('recondit', 'непонятный'),
            ('melt', 'расплав'),
            ('reconnaissance', 'разведка'),
            ('reprobate', 'негодяй'),
            ('daffodil', 'нарцисс'),
            ('bagel', 'бублик')
        ]
        for en_word, ru_translate in test_words:
            self.add_word(en_word, ru_translate)


if __name__ == '__main__':
    TGBotDB().create_db()
    TGBotDB().delete_tables()
    TGBotDB().create_tables()
    TGBotDB().add_test_data()
