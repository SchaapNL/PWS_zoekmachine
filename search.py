from nltk.stem import PorterStemmer

import DatabaseManager
import Utils
import time

def main():
    start_time = time.time()
    punctuation = ['.', ',', ':', ';', '\"', '\'', '!', '?', '/', '(', ')', '[', ']', '{', '}', '-', '^', '–']

    # commonWords = ['the', 'of', 'and', 'in', 'a', 'in', 'from', 'to', 'is', 'on', 'or', 'by', 'with', 'as', 'are',
    # 'for', 'that', 'may', 'thi', 'be', 'it', 'have', 'can', 'but', 'than']

    query = ''

    ## filter punctuation
    for i in punctuation:
        query = query.replace(i, ' ')

    Utils.stem_freq_words(query)

    db = DatabaseManager
    con = db.connect_to_database('zoekmachine.db')

    db.close_connection(con)

    print('The search took %f' % (time.time()- start_time))


if __name__ == '__main__':
    main()
