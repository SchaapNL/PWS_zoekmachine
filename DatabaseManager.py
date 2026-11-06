import sqlite3
import os
import time

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
                domain_id INTEGER,
                last_crawled INTEGER,
                last_scanned_sites INTEGER,
                FOREIGN KEY (domain_id) REFERENCES domain (domain_id)
            );
            ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS word_frequencies (
                website_id INTEGER NOT NULL,
                word TEXT NOT NULL,
                hoeveelheid REAL NOT NULL,
                FOREIGN KEY (website_id) REFERENCES websites (website_id)
            );
            ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authors (
                website_id INTEGER NOT NULL,
                author TEXT NOT NULL,
                score INTEGER,
                FOREIGN KEY (website_id) REFERENCES websites (website_id)
            );
            ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS links (
                website_id INTEGER NOT NULL,
                link_id INTEGER NOT NULL,
                same_domain BOOLEAN NOT NULL,
                FOREIGN KEY (website_id) REFERENCES websites (website_id)
            );
            ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS websites (
                website_id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain_id INTEGER NOT NULL,
                link TEXT NOT NULL,
                last_crawled INTEGER,
                last_scanned_sites INTEGER,
                FOREIGN KEY (domain_id) REFERENCES domain (domain_id)
            );
            ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS domains (
            domain_id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain_name TEXT NOT NULL,
            domain_registration INTEGER,
            domain_last_changed INTEGER,
            last_updated INTEGER
            );
            ''')

        connection.commit()

    except Exception as e:
        print("create_tables failed")
        print(e)

def insert_website(connection, website):
    if type(website) != str:
        raise ValueError('websites must be a str')

    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO websites (link) VALUES (?)",
            (website,)
        )

        connection.commit()

    except Exception as e:
        print('insert_websites failed')
        print(e)

def update_last_crawled(connection, website_id, last_crawled):
    if type(website_id) != int:
        raise ValueError('websiteId must be an int')
    if type(last_crawled) != int:
        raise ValueError('last_crawled must be an int')

    try:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE websites SET last_crawled = ? WHERE website_id = ?",
            (last_crawled, website_id)
        )

        connection.commit()

    except Exception as e:
        print('update_last_crawled failed')
        print(e)

def update_last_scanned_sites(connection, website_id, last_crawled_sites):
    if type(website_id) != int:
        raise ValueError('websiteId must be an int')
    if type(last_crawled_sites) != int:
        raise ValueError('last_crawled_sites must be an int')

    try:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE websites SET last_scanned_sites = ? WHERE website_id = ?",
            (last_crawled_sites, website_id)
        )

        connection.commit()

    except Exception as e:
        print('update_last_crawled_sites failed')
        print(e)


def insert_word_frequencies(connection, website_id, woord_freq_dict):
    if type(woord_freq_dict) != dict:
        raise ValueError('wrong type for woord_freq_dict')
    if type(website_id) != int:
        raise ValueError('website_id must be a int')

    try:
        cursor = connection.cursor()

        for woord, freq in woord_freq_dict.items():
            cursor.execute('INSERT INTO word_frequencies (website_id, word, hoeveelheid) VALUES (?, ?, ?)',
                           (website_id, woord, freq)
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

        return [row[0] for row in cursor.fetchall()]

    except Exception as e:
        print(e)

def get_websites_to_crawl(connection):
    try:
        cursor = connection.cursor()

        week_ago = time.time() - 7*24*60*60
        cursor.execute(f'SELECT website_id, link FROM websites WHERE last_crawled IS NULL OR last_crawled < {week_ago}')

        return [list(row) for row in cursor.fetchall()]

    except Exception as e:
        print(e)

def get_site_to_scan_links(connection):
    try:
        cursor = connection.cursor()

        week_ago = time.time() - 7*24*60*60
        cursor.execute(f'SELECT website_id, link FROM websites WHERE last_scanned_sites IS NULL OR last_crawled < {week_ago}')

        return cursor.fetchone()

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

def get_last_crawled(connection, website_id):
    if type(website_id) != int:
        raise ValueError('website_id must be an int')

    try:
        cursor = connection.cursor()
        cursor.execute('SELECT last_crawled FROM websites WHERE website_id = ?', (website_id,))

        read = cursor.fetchone()
        if read is None:
            return None
        return read[0]

    except Exception as e:
        print(e)

def get_last_scanned_site(connection, website_id):
    if type(website_id) != int:
        raise ValueError('website_id must be an int')

    try:
        cursor = connection.cursor()
        cursor.execute('SELECT last_scanned_sites FROM websites WHERE website_id = ?', (website_id,))

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

def clear_word_freq(connection, website_id):
    if type(website_id) != int:
        raise ValueError('website_id must be an int')

    try:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM word_frequencies WHERE website_id = ?', (website_id,))

        return

    except Exception as e:
        print('clear_site failed')
        print(e)

def insert_author(connection, website_id, author, score):
    if type(author) != str:
        raise ValueError('author must be a string')
    if type(website_id) != int:
        raise ValueError('websiteId must be a int')

    try:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO authors (website_id, author, score) VALUES (?, ?, ?)',
                       (website_id, author, score))

        connection.commit()

    except Exception as e:
        print('insert_author failed')
        print(e)

def clear_author(connection, website_id):
    if type(website_id) != int:
        raise ValueError('websiteId must be an int')

    try:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM authors WHERE website_id = ?', (website_id,))

        connection.commit()
        return

    except Exception as e:
        print('clear_author failed')
        print(e)

def get_author(connection, website_id):
    if type(website_id) != int:
        raise ValueError('websiteId must be an int')

    try:
        cursor = connection.cursor()
        cursor.execute('SELECT author FROM authors WHERE website_id = ?', (website_id,))

        return cursor.fetchone()

    except Exception as e:
        print('get_author failed')
        print(e)

def get_unrated_authors(connection):
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT website_id, author FROM authors WHERE score IS NULL')

        return cursor.fetchall()

    except Exception as e:
        print('get_unrated_authors failed')
        print(e)

def set_author_score(connection, website_id, author, score):
    if type(website_id) != int:
        raise ValueError('websiteId must be an int')
    if type(author) != str:
        raise ValueError('author must be a string')
    if type(score) != float:
        raise ValueError('score must be an int')

    try:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE authors SET score = ? WHERE website_id = ? AND author = ?",
            (score, website_id, author)
        )

        connection.commit()

    except Exception as e:
        print('set_author_score failed')
        print(e)

def get_website_score(connection, weights):
    if type(weights) != list:
        raise ValueError('weights must be a list')

    if not weights:
        return []

    whens = "".join("WHEN ? THEN ?" for _ in weights)

    params = []
    for weight in weights:
        params.append(weight[0])
        params.append(weight[1])

    try:
        cursor = connection.cursor()
        cursor.execute(f"""
            SELECT website_id, SUM(hoeveelheid / CASE word {whens} ELSE 0 END) AS score
            FROM word_frequencies
            GROUP BY website_id
            HAVING score IS NOT NULL
            ORDER BY score DESC""", params)
        return cursor.fetchall()

    except Exception as e:
        print('get_website_score failed')
        print(e)

def get_weights(connection, words):
    if type(words) != list:
        raise ValueError('words must be a list')

    if not words:
        return []

    try:
        cursor = connection.cursor()

        placeholders = ','.join(['?'] * len(words))
        cursor.execute(f"""SELECT word, count(*) 
                FROM word_frequencies 
                WHERE word IN ({placeholders})
                GROUP BY word""", words)

        return cursor.fetchall()

    except Exception as e:
        print('get_weights failed')
        print(e)

def get_authors_from_site_ids(connection, site_ids):
    if type(site_ids) != list:
        raise ValueError('site_ids must be a list')
    if not site_ids:
        return []

    try:
        cursor = connection.cursor()

        placeholders = ','.join(['?'] * len(site_ids))

        cursor.execute(f"""SELECT * 
        FROM authors 
        WHERE website_id IN ({placeholders})""", site_ids)

        return cursor.fetchall()

    except Exception as e:
        print('get_authors_from_site_ids failed')
        print(e)

def insert_domain(connection, domain):
    if type(domain) != str:
        raise ValueError('domain must be a string')

    try:
        cursor = connection.cursor()
        cursor.execute(f"""INSERT INTO domains (domain_name) VALUES (?)""", (domain,))
        connection.commit()

    except Exception as e:
        print('insert_domain failed')
        print(e)

def update_domain_info(connection, domain_id, domain_registration, domain_last_change):
    if type(domain_id) != int:
        raise ValueError('domainId must be an int')
    if type(domain_registration) != int:
        raise ValueError('domainRegistration must be an int')
    if type(domain_last_change) != int:
        raise ValueError('domainLastChange must be an int')

    try:
        cursor = connection.cursor()
        cursor.execute(f"""UPDATE domains 
                SET domain_registration = ?, 
                    domain_last_changed = ?, 
                    last_updated = ?
                WHERE domain_id = ?""",
                       (domain_registration, domain_last_change, int(time.time()), domain_id,))
        connection.commit()

    except Exception as e:
        print('update_domain_info failed')
        print(e)

def insert_link(connection, website_id, link_id):
    if type(website_id) != int:
        raise ValueError('websiteId must be an int')
    if type(link_id) != int:
        raise ValueError('link must be an int')

    try:
        cursor = connection.cursor()
        cursor.execute(f"""INSERT INTO links (website_id, link_id) VALUES (?, ?) """,
                       (website_id, link_id))

        connection.commit()

    except Exception as e:
        print('insert_link failed')
        print(e)

def get_website_ids_from_links(connection, links):
    if type(links) != list:
        raise ValueError('links must be a list')
    if not links:
        return []

    try:
        cursor = connection.cursor()

        placeholders = ','.join(['?'] * len(links))

        cursor.execute(f"""SELECT website_id, link
            FROM websites
            WHERE link IN ({placeholders})""", links)

        return cursor.fetchall()

    except Exception as e:
        print('get_website_ids_from_links failed')
        print(e)

def insert_website_links(connection, website_id, link_list):
    if type(link_list) != list:
        raise ValueError('link_list must be a list')
    if not link_list:
        return []

    try:
        cursor = connection.cursor()

        cursor.executemany("""INSERT INTO links (website_id, link_id, same_domain) VALUES (?, ?, ?) """,
                           [(website_id, link_info[0], link_info[1]) for link_info in link_list])
        connection.commit()

    except Exception as e:
        print('insert_website_links failed')
        print(e)

def get_domain_id(connection, domain):
    if type(domain) != str:
        raise ValueError('domain must be a string')

    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT domain_id FROM domains WHERE domain_name = (?)""", (domain,))
        read = cursor.fetchone()
        if read is None:
            return None
        return read[0]

    except Exception as e:
        print('get_domain_id failed')
        print(e)

def update_website_domain(connection, website_id, domain_id):
    if type(website_id) != int:
        raise ValueError('websiteId must be an int')
    if type(domain_id) != int:
        raise ValueError('domainId must be an int')

    try:
        cursor = connection.cursor()
        cursor.execute(f"""UPDATE websites SET domain_id = ? WHERE website_id = ?""", (domain_id, website_id))
        connection.commit()

    except Exception as e:
        print('update_website_domain failed')
        print(e)

def get_or_create_domain_id(connection, domain):
    domain_id = get_domain_id(connection, domain)
    if domain_id is not None:
        return domain_id

    insert_domain(connection, domain)
    return get_domain_id(connection, domain)

def get_or_create_website_id(connection, website):
    website_id = get_website_id(connection, website)
    if website_id is not None:
        return website_id

    insert_website(connection, website)
    return get_website_id(connection, website)

def get_domains_to_update(con):
    try:
        week_ago = time.time() - 7*24*60*60

        cursor = con.cursor()
        cursor.execute(f"""SELECT domain_id, domain_name 
            FROM domains 
            WHERE last_updated IS NULL OR last_updated < {week_ago}""")
        read = cursor.fetchall()

        if read is None:
            return []
        return read

    except Exception as e:
        print('get_domains_to_update failed')
        print(e)

def get_website_score2(connection, words):
    if type(words) != list:
        raise ValueError('words must be a list')

    if not words:
        print("AHHHHHH")
        return []

    try:
        placeholders = ','.join(['?'] * len(words))

        cursor = connection.cursor()
        cursor.execute(f"""
            WITH weights AS (
                SELECT word, COUNT(*) AS weight
                FROM word_frequencies
                WHERE word IN ({placeholders})
                GROUP BY word
            ),
            scores AS (
                SELECT wf.website_id,
                       SUM(wf.hoeveelheid / weights.weight) AS score
                FROM word_frequencies wf
                JOIN weights ON weights.word = wf.word
                GROUP BY wf.website_id
            ),
            author_list AS (
                SELECT website_id,
                GROUP_CONCAT(author || ': ' || COALESCE(score, 'N/A'), '; ') AS authors
                FROM authors
                GROUP BY website_id
            ),
            links_count AS (
                SELECT website_id,
                    SUM(same_domain = 1) AS same_domain,
                    SUM(same_domain = 0) AS other_domain
                FROM links
                GROUP BY website_id
            ),
            back_links_count AS (
            SELECT link_id,
                SUM(same_domain = 1) AS same_domain,
                SUM(same_domain = 0) AS other_domain
            FROM links
            GROUP BY link_id
            )
            
            Select w.link, s.score, a.authors, d.domain_registration, d.domain_last_changed, 
                l.same_domain, l.other_domain, b.same_domain, b.other_domain
            FROM websites w
            LEFT JOIN scores s ON s.website_id = w.website_id
            LEFT JOIN author_list a ON a.website_id = w.website_id
            LEFT JOIN domains d ON d.domain_id = w.domain_id
            LEFT JOIN links_count l ON l.website_id = w.website_id
            LEFT JOIN back_links_count b ON b.link_id = w.website_id
            
            ORDER BY s.score DESC
            LIMIT 50
            """, words)
        return cursor.fetchall()



    except Exception as e:
        print('get_website_score failed')
        print(e)


def close_connection(connection):
    try:
        connection.close()

    except Exception as e:
        print('close_connection failed')
        print(e)