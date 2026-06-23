from nltk.stem import PorterStemmer

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

    stem_freq_words(query)

    end_time = time.time()
    pycurl_time = end_time - start_time
    print('The pycurl_get takes %f' % pycurl_time)

def stem_freq_words(text):
    ps = PorterStemmer()
    array1 = text.split()
    array2 = {}

    if type(text) != str:
        raise ValueError('dat was geen string jouw computer doet nu kaboem')
    else:
        for word in array1:
            word = ps.stem(word)
            if word in array2:
                array2[word] = (array2[word]*len(array1) + 1) / len(array1)
            else:
                array2[word] = 1 / len(array1)

    array2 = {k: v for k, v in sorted(array2.items(), key=lambda item: item[1])}

    for word in array2:
        print(word + ' ' + str(array2[word]))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
