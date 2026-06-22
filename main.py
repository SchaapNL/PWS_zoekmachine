import pycurl
from bs4 import BeautifulSoup
from io import BytesIO

import time

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

    # voor als we ooit het verder willen laten zoeken.
    # for link in html.find_all('a'):
    #     print(link.get('href'))

    # print(html.get_text())

def main():
    start_time = time.time()

    url = 'https://en.wikipedia.org/wiki/Leonhard_Euler'
    text = get_DOM_from_URL(url)
    count_words(text)

    end_time = time.time()
    pycurl_time = end_time - start_time

    print('The pycurl_get takes %f' % pycurl_time)

def count_words(text):
   array = {}
   for word in text.split():
      if word in array:
         array[word] += 1
      else:
         array[word] = 1

   for word in array:
      print(word + ' ' + str(array[word]))

if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

