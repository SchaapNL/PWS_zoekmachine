import string

import pycurl
from bs4 import BeautifulSoup
from io import BytesIO
from nltk.stem import PorterStemmer

import time
import DatabaseManager
import Utils

def main():
    start_time = time.time()
    punctuation = ['.', ',', ':', ';', '\"', '\'', '!', '?', '/', '(', ')', '[', ']', '{', '}', '-', '^', '–']

    # commonWords = ['the', 'of', 'and', 'in', 'a', 'in', 'from', 'to', 'is', 'on', 'or', 'by', 'with', 'as', 'are',
    # 'for', 'that', 'may', 'thi', 'be', 'it', 'have', 'can', 'but', 'than']

    db = DatabaseManager
    con = db.connect_to_database('zoekmachine.db')
    db.create_tables(con)

    sites = ['https://nl.wikipedia.org/wiki/Bob_de_Bouwer', 'https://en.wikipedia.org/wiki/Bob_the_Builder']

    for site in sites:
        # print(db.get_website_id(con, site))
        if db.get_website_id(con, site) is not None:
            continue

        text = Utils.get_DOM_from_URL(site)

        for i in punctuation:
            text = text.replace(i, ' ')

        woord_freq_dict = Utils.stem_freq_words(text)

        db.insert_websites(con, site)
        site_id = db.get_website_id(con, site)
        db.insert_word_frequencies(con, site_id, woord_freq_dict)
        print('crawling %s' % site)


    db.close_connection(con)

    end_time = time.time()
    f_time = end_time - start_time

    print('crawl successful, duurde %f' % f_time)

if __name__ == '__main__':
    main()