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
        cursor.execute('SELECT website_id FROM websites WHERE link = ?', (website,))

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

def get_words_frequencies_list(connection, word_list):
    if type(word_list) != list:
        raise ValueError('words must be a list')
    if len(word_list) == 0:
        raise ValueError('words must not be empty')

    try:
        cursor = connection.cursor()

        placeholders = ','.join(['?'] * len(word_list))
        cursor.execute(f"SELECT word, hoeveelheid FROM word_frequencies WHERE word IN ({placeholders})", word_list)

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

def close_connection(connection):
    try:
        connection.close()

    except Exception as e:
        print('close_connection failed')
        print(e)