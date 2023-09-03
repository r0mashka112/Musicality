from bs4 import BeautifulSoup
import requests, random, config


def getURL():
    URL = config.URL + str(random.randint(1, 10))

    page = requests.get(URL)

    soup = BeautifulSoup(page.text, 'html.parser')

    data = soup.find_all('li', class_ = 'item')

    rand_Item = random.randint(0, 110)

    info = data[rand_Item].find('span', class_ = 'artist').text + \
        ' - ' + data[rand_Item].find('span', class_ = 'track').text

    url = data[rand_Item].find('li', class_ = 'play')['data-url']

    return info, url
