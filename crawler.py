import string

import pycurl
from bs4 import BeautifulSoup
from io import BytesIO
from nltk.stem import PorterStemmer

import time
import DatabaseManager
import Utils
from DatabaseManager import insert_word_frequencies

def filter_links(links):
    for link in links:
        remove_link = False
        if link.find('wikipedia.org') != -1:
            # filter non english wiki pages
            if link.find('en.wikipedia.org') == -1:
                remove_link = True

            # filter non informative wiki pages
            filters = ['Portal:', 'Help:', 'Special:', 'Talk:', 'File:', 'title=', 'action=']
            for f in filters:
                if link.find(f) != -1:
                    remove_link = True
        if remove_link:
            links[links.index(link)] = None

    while None in links:
        links.remove(None)
    return links


def main():
    start_time = time.time()

    db = DatabaseManager
    con = db.connect_to_database('zoekmachine.db')
    db.create_tables(con)

    sites_in_db = [row[0] for row in db.get_all_website_ids(con)]
    sites = []
    for IDs in sites_in_db:
        sites.append(db.get_website_url(con, IDs))

    if len(sites) == 0:
        sites = ['https://en.wikipedia.org/wiki/Bob_the_Builder']


    for site in sites:
        print(db.get_website_id(con, site))

        end_of_root = site.find('/', 8)
        url_root = site if end_of_root == -1 else site[:end_of_root]

        text = Utils.get_DOM_from_URL(site)
        found_links = []

        for link in text.find_all('a'):
            #print(link.get('href'))
            found_links.append(link.get('href'))

        for link in found_links:
            if not 'https://' in link and not 'http://' in link:
                if link.find('/') == 0:
                    found_links[found_links.index(link)] = url_root + link
                else:
                    found_links[found_links.index(link)] = None

        while None in found_links:
            found_links.remove(None)

        found_links = filter_links(found_links)
        print(found_links)
        print(len(found_links))

        # temporary ---
        if db.get_website_id(con, site) is None:
            text = Utils.get_text_from_URL(site)
            text = Utils.remove_punctuation(text)

            word_freq_dict = Utils.stem_freq_words(text)

            db.insert_websites(con, site)
            site_id = db.get_website_id(con, site)
            db.insert_word_frequencies(con, site_id, word_freq_dict)
        # ---

        if len(sites) == 1:
            for link in found_links:
                if db.get_website_id(con, link) is None:
                    # add freq
                    text = Utils.get_text_from_URL(link)

                    if text is not None:
                        text = Utils.remove_punctuation(text)

                        word_freq_dict = Utils.stem_freq_words(text)

                        db.insert_websites(con, link)
                        site_id = db.get_website_id(con, link)
                        db.insert_word_frequencies(con, site_id, word_freq_dict)
                        # print('crawling %s' % site)


        #db.update_last_crawled(con, db.get_website_id(con, site), time.time())


    db.close_connection(con)

    end_time = time.time()
    f_time = end_time - start_time

    print('crawl successful, took %f' % f_time)

if __name__ == '__main__':
    main()