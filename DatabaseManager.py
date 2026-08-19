import sqlite3

def connect_to_database(db_path):
    if type(db_path) != str:
        raise ValueError('db_path must be a string')

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
                link TEXT NOT NULL
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
        websiteId = cursor.execute('SELECT website_id FROM websites WHERE link = ?', (website,))

        connection.commit()
        return websiteId.fetchone()[0]

    except Exception as e:
        print(e)


def get_words_frequencies_url(connection, websiteId):
    if type(websiteId) != int:
        raise ValueError('websiteId must be a int')

    try:
        cursor = connection.cursor()
        words = cursor.execute('SELECT word, hoeveelheid FROM word_frequencies WHERE website_id = ?', (websiteId,))

        connection.commit()
        return words.fetchall()

    except Exception as e:
        print('get_words_frequencies failed')
        print(e)

def get_words_frequencies_list(connection, words):
    if type(words) != list:
        raise ValueError('words must be a list')

    try:
        cursor = connection.cursor()

        placeholders = ",".join("?" for _ in words)

        woordFreqDict = cursor.execute(f'SELECT word, hoeveelheid FROM word_frequencies WHERE website_id IN ({placeholders})', (words[0], words[1], words[2],))

        connection.commit()
        return woordFreqDict.fetchall()

    except Exception as e:
        print('get_words_frequencies_list failed')
        print(e)


def close_connection(connection):
    try:
        connection.close()

    except Exception as e:
        print('close_connection failed')
        print(e)