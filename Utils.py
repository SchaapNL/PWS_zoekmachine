import pycurl

from bs4 import BeautifulSoup
from io import BytesIO
from nltk.stem import PorterStemmer


#
#   Returns the text stripped of punctuation.
#
punctuation = ['.', ',', ':', ';', '\"', '\'', '!', '?', '/', '(', ')', '[', ']', '{', '}', '-', '^', '–']
def remove_punctuation(text):
    for i in punctuation:
        text = text.replace(i, ' ')
    return text

#
#   Returns the text of in the html of a site.
#
def get_DOM_from_URL(url):
    b = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, b)
    c.perform()
    c.close()
    body = b.getvalue()

    html = BeautifulSoup(body, 'html.parser')
    return html.get_text()


#
#   Returns an array of the frecency of each word divided by the total amount of words in the text.
#
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

    return array2


def stem_words(query):
    if type(query) != str:
        raise ValueError('dat was geen string jouw computer doet nu kaboem')

    ps = PorterStemmer()
    array1 = query.split()

    for i in range(len(array1)):
        array1[i] = ps.stem(array1[i])

    return array1