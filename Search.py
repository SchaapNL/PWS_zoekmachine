from nltk.stem import PorterStemmer

import DatabaseManager
import Utils
import time

def search(query):
    db = DatabaseManager
    con = db.connect_to_database('zoekmachine.db')

    query = Utils.remove_punctuation(query)
    query = Utils.stem_words(query)

    # run through words in query and get website id of websites containing a searched word, put id's in array
    # per id in the array, loop through searched words and get frequency in the website,
    # divide by the word rarity and put in dict with key = id and value = freq/rarity, or + it if there is already a value

    sites_with_words = []

    for word in query:
        for id in [row[0] for row in db.get_sites_with_word(con, word)]:
            if id not in sites_with_words:
                sites_with_words.append(id)

    #print(sites_with_words)

    website_imp = {}

    for web_id in sites_with_words:
        for word in query:
            word_freq = db.get_word_frequency(con, web_id, word)
            if word_freq != 0:
                if web_id not in website_imp:
                    website_imp[web_id] = word_freq / db.get_amount_of_sites_with_word(con, word)
                else:
                    website_imp[web_id] += word_freq / db.get_amount_of_sites_with_word(con, word)
                #print(web_id)
                #print(word)
                #print(website_imp[web_id])

    website_imp = {k: v for k, v in sorted(website_imp.items(), key=lambda item: item[1], reverse=True)}
    #print(website_imp)

    search_results = []
    for website in website_imp:
        result_id = [k for k, v in website_imp.items() if v == website_imp[website]][0]
        search_results.append(db.get_website_url(con, result_id))

    db.close_connection(con)
    return search_results

def main():
    start_time = time.time()

    query = ('bob de bouwer')
    search_results = search(query)

    if len(search_results) == 0:
        print('no results')
    else:
        print(search_results)

    print('The search took %f' % (time.time()- start_time))

if __name__ == '__main__':
    main()
