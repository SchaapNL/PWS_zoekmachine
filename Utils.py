import pycurl
import time
import json

from bs4 import BeautifulSoup
from io import BytesIO
from nltk.stem import PorterStemmer
from urllib.parse import urlsplit, urlunsplit, quote
from trafilatura import fetch_url, extract


#
#   Returns the text stripped of punctuation.
#
punctuation = ['.', ',', ':', ';', '\"', '\'', '!', '?', '/', '(', ')', '[', ']', '{', '}', '-', '^', '–']
def remove_punctuation(text):
    for i in punctuation:
        text = text.replace(i, ' ')
    return text

# Keeping this for if we want to set our own user agent since I can't figure it out using trafilatura
#
#   Returns the HTML in DOM format.
#
def get_DOM_from_URL(url):
    url = encode_url(url)
    b = BytesIO()
    c = pycurl.Curl()
    try:
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, b)
        c.setopt(pycurl.USERAGENT, "moffel")

        c.setopt(c.CONNECTTIMEOUT, 5)
        c.setopt(c.TIMEOUT, 10)

        c.perform()
        content_type = c.getinfo(c.CONTENT_TYPE)
    except (UnicodeEncodeError, pycurl.error) as e:
        print(f"Skipping bad URL: {url!r} ({e})")
        c.close()
        return None
    c.close()
    body = b.getvalue()

    encoding = None
    if content_type and 'charset=' in content_type:
        encoding = content_type.split('charset=')[-1].strip()

    html = BeautifulSoup(body, 'html.parser', from_encoding=encoding)
    return html

def encode_url(url):
    parts = urlsplit(url)
    path = quote(parts.path, safe="/%")
    query = quote(parts.query, safe="=&%")
    fragment = quote(parts.fragment, safe="%")
    return urlunsplit((parts.scheme, parts.netloc, path, query, fragment))


  # Returns the text of in the html of a site.

def get_text_from_URL(url):
    html = get_DOM_from_URL(url)
    if html is not None:
        return html.text
    else:
        return None

def get_website_information(url):
    if type(url) != str:
        raise TypeError("url must be a string.")

    response = fetch_url(url)
    if response is None:
        print(f"{url} didn't respond.")
        return None

    extracted = extract(response, output_format="json", with_metadata=True)

    if extracted is None:
        print(f"Failed to extract data from {url}.")
        return None

    data = json.loads(extracted)

    DOM = BeautifulSoup(response, "html.parser")

    found_links = [links.get('href') for links in DOM.findAll('a')]

    return {
        "text": data.get("raw_text") or None,
        "title": data.get("title") or None,
        "authors": data.get("author") or None,
        "date": data.get("date") or None,
        "links": found_links
    }

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

def get_root_url(url):
    # gets the first / after the scheme declaration.
    end_of_root = url.find('/', len("https://"))
    # If there are no other /'s in the url it returns -1 ,and you got the complete link otherwise we cut if off after
    # the next / is found

    return url if end_of_root == -1 else url[:end_of_root]