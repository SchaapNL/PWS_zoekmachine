import sqlite3
import os

def connect_to_database(db_name):
    if type(db_name) != str:
        raise ValueError('db_path must be a string')

    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, db_name)

    try:
        connection = sqlite3.connect(db_path)
        return connection

    except Exception as e:
        print('connect_to_database failed')
        print(e)
        return None

def create_tables(connection):
    try:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS websites (
                website_id INTEGER PRIMARY KEY AUTOINCREMENT,
                link TEXT NOT NULL,
                last_crawled INTEGER
            );
            ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS word_frequencies (
                website_id INTEGER NOT NULL,
                word TEXT NOT NULL,
                hoeveelheid REAL NOT NULL
            );
            ''')

        connection.commit()

    except Exception as e:
        print("create_tables failed")
        print(e)

def insert_websites(connection, websites):
    if type(websites) != str:
        raise ValueError('websites must be a str')

    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO websites (link) VALUES (?)",
            (websites,)
        )

        connection.commit()

    except Exception as e:
        print('insert_websites failed')
        print(e)

def update_last_crawled(connection, websiteId, last_crawled):
    if type(websiteId) != int:
        raise ValueError('websiteId must be an int')

    try:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE websites SET last_crawled = ? WHERE website_id = ?",
            (last_crawled, websiteId)
        )

        connection.commit()

    except Exception as e:
        print('update_last_crawled failed')
        print(e)

def insert_word_frequencies(connection, websiteId , woordFreqDict):
    if type(woordFreqDict) != dict:
        raise ValueError('wrong type for woordFreqDict')
    if type(websiteId) != int:
        raise ValueError('websiteId must be a int')

    try:
        cursor = connection.cursor()

        for woord, freq in woordFreqDict.items():
            cursor.execute('INSERT INTO word_frequencies (website_id, word, hoeveelheid) VALUES (?, ?, ?)',
                           (websiteId, woord, freq)
            )
        connection.commit()

    except Exception as e:
        print(e)

def get_website_id(connection, website):
    if type(website) != str:
        raise ValueError('website must be a str')

    try:
        cursor = connection.cursor()
        cursor.execute('SELECT website_id FROM websites WHERE link = ?', (website,))

        read = cursor.fetchone()
        if read is None:
            return None
        return read[0]

    except Exception as e:
        print(e)

def get_all_website_ids(connection):
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT website_id FROM websites')

        return cursor.fetchall()

    except Exception as e:
        print(e)

def get_website_url(connection, website_id):
    if type(website_id) != int:
        raise ValueError('website_id must be an int')

    try:
        cursor = connection.cursor()
        cursor.execute('SELECT link FROM websites WHERE website_id = ?', (website_id,))

        read = cursor.fetchone()
        if read is None:
            return None
        return read[0]

    except Exception as e:
        print(e)

def get_words_frequencies_url(connection, website_id):
    if type(website_id) != int:
        raise ValueError('websiteId must be a int')

    try:
        cursor = connection.cursor()
        cursor.execute('SELECT word, hoeveelheid FROM word_frequencies WHERE website_id = ?', (website_id,))

        connection.commit()
        return cursor.fetchall()

    except Exception as e:
        print('get_words_frequencies failed')
        print(e)

def get_word_frequency(connection, website_id, word):
    if type(website_id) != int:
        raise ValueError('websiteId must be a int')
    if type(word) != str:
        raise ValueError('word must be a str')

    try:
        cursor = connection.cursor()
        cursor.execute('SELECT hoeveelheid FROM word_frequencies WHERE website_id = ? and word = ?', (website_id, word))

        connection.commit()
        read = cursor.fetchone()
        if read is None:
            return 0
        return read[0]

    except Exception as e:
        print('get_word_frequency failed')
        print(e)

def get_words_frequencies_list(connection, word_list):
    if type(word_list) != list:
        raise ValueError('words must be a list')
    if len(word_list) == 0:
        raise ValueError('words must not be empty')

    try:
        cursor = connection.cursor()

        placeholders = ','.join(['?'] * len(word_list))
        cursor.execute(f"SELECT website_id, word, hoeveelheid FROM word_frequencies WHERE word IN ({placeholders})", word_list)

        return cursor.fetchall()

    except Exception as e:
        print('get_words_frequencies_list failed')
        print(e)

def get_amount_of_websites(connection):
    try:
        cursor = connection.cursor()

        cursor.execute('SELECT COUNT(website_id) FROM websites')

        return cursor.fetchone()[0]

    except Exception as e:
        print('get_amount_of_websites failed')
        print(e)

def get_amount_of_sites_with_word(connection, word):
    if type(word) != str:
        raise ValueError('word must be a str')

    try:
        cursor = connection.cursor()

        cursor.execute('SELECT COUNT(*) FROM word_frequencies WHERE word = ?', (word,))

        return cursor.fetchone()[0]

    except Exception as e:
        print('get_amount_of_sites_with_word failed')
        print(e)

def get_sites_with_word(connection, word):
    if type(word) != str:
        raise ValueError('word must be a str')

    try:
        cursor = connection.cursor()

        cursor.execute('SELECT website_id FROM word_frequencies WHERE word = ?', (word,))

        return cursor.fetchall()

    except Exception as e:
        print('get_sites_with_word failed')
        print(e)

def close_connection(connection):
    try:
        connection.close()

    except Exception as e:
        print('close_connection failed')
        print(e)