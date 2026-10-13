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
    links.sort()
    last_robot_txt = {"root": str, "robots.txt": list}
    for link in links:
        if 'wikipedia.org' in link and 'en.wikipedia.org' not in link:
            links[links.index(link)] = None
            continue

        root_url = get_root_url(link)
        if root_url == last_robot_txt['root']:
            disallowed_urls = last_robot_txt['robots.txt']
        else:
            disallowed_urls = get_disallowed_urls(root_url)
            last_robot_txt = {"root": root_url, "robots.txt": disallowed_urls}

        for disallowed_url in disallowed_urls:
            if link.startswith(disallowed_url):
                links[links.index(link)] = None
                continue

    while None in links:
        links.remove(None)

    return links



def get_root_url(url):
    # gets the first / after the scheme declaration.
    end_of_root = url.find('/', len("https://"))
    # If there are no other /'s in the url it returns -1 ,and you got the complete link otherwise we cut if off after
    # the next / is found

    return url if end_of_root == -1 else url[:end_of_root]

def get_disallowed_urls(site):
    root_url = get_root_url(site)
    robots_txt = Utils.get_text_from_URL(root_url + "/robots.txt")

    if robots_txt is None:
        return []

    correct_user_agent = False
    disallowed = []
    for line in robots_txt.split("\n"):
        if line is None: continue

        if line.startswith("User-agent: "):
            if line[len("User-agent: ") :] == "*" or line[len("User-agent: ") :] == "moffel":
                correct_user_agent = True

            else:
                correct_user_agent = False

        if correct_user_agent:
            if line.startswith("Disallow: "):
                disallowed.append(root_url + line[len("Disallow: "):])

    return disallowed

def main():
    start_time = time.time()

    db = DatabaseManager
    con = db.connect_to_database('zoekmachine.db')
    db.create_tables(con)

    sites_in_db = [row[0] for row in db.get_all_website_ids(con)]
    sites = []
    for ID in sites_in_db:
        if db.get_last_crawled(con, ID) is None or time.time() - db.get_last_crawled(con,ID) > 7*24*60*60: # crawls again after a week
            sites.append(db.get_website_url(con, ID))

    if len(sites_in_db) == 0:
        sites = ['https://en.wikipedia.org/wiki/Bob_the_Builder']



    for site in sites:
        print(db.get_website_id(con, site))

        url_root = get_root_url(site)

        text = Utils.get_DOM_from_URL(site)
        found_links = []

        for link in text.find_all('a'):
            found_links.append(link.get('href'))

        for link in found_links:
            if not 'https://' in link and not 'http://' in link:
                if link[:1] == "/":
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


        db.update_last_crawled(con, db.get_website_id(con, site), time.time())


    db.close_connection(con)

    end_time = time.time()
    f_time = end_time - start_time

    print('crawl successful, took %f' % f_time)

if __name__ == '__main__':
    main()