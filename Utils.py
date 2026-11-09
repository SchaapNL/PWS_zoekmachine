import pycurl
import json
import tldextract

from datetime import datetime
from bs4 import BeautifulSoup
from io import BytesIO
from nltk.stem import PorterStemmer
from trafilatura import fetch_url, extract

import DomainInfoModule

#
#   Returns the text stripped of punctuation.
#
punctuation = ['.', ',', ':', ';', '\"', '\'', '!', '?', '/', '(', ')', '[', ']', '{', '}', '-', '^', '–']
def remove_punctuation(text):
    for i in punctuation:
        text = text.replace(i, ' ')
    return text

def api_call(api_call, header):
    b = BytesIO()
    c = pycurl.Curl()

    if header is not None:
        c.setopt(c.HTTPHEADER, header)

    c.setopt(c.URL, api_call)
    c.setopt(c.WRITEDATA, b)
    c.setopt(pycurl.USERAGENT, "moffel")
    c.setopt(c.FOLLOWLOCATION, True)
    c.setopt(c.TIMEOUT, 10)

    try:
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
    finally:
        c.close()

    if status == 404:
        print(f"No record found for {api_call}")
        return None

    if status != 200:
        print(f"HTTP status {status} for {api_call}")
        return None

    return json.loads(b.getvalue().decode("utf-8"))

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

    dom = BeautifulSoup(response, "html.parser")

    found_links = [links.get('href') for links in dom.findAll('a')]

    return {
        "text": data.get("raw_text") or None,
        "title": data.get("title") or None,
        "authors": data.get("author") or None,
        "date": data.get("date") or None,
        "links": found_links,
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

def get_domain(url_or_host):
    ext = tldextract.extract(url_or_host)

    if not ext.domain or not ext.suffix:
        return None

    return f"{ext.domain}.{ext.suffix}"

def timestamp_to_epoch(timestamp):
    return int(datetime.fromisoformat(timestamp).timestamp())

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