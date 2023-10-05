from bs4 import BeautifulSoup
import requests, re, random, config


async def getAudio() -> (dict, str):
    page = requests.get(config.URL + str(random.randint(1, 10)))

    soup = BeautifulSoup(page.text, 'html.parser')

    data = soup.find_all('li', class_ = 'item')

    rand_Item = random.randint(0, 109)

    info = {
        'artist' : data[rand_Item].find('span', class_ = 'artist').text, 
        'track' : data[rand_Item].find('span', class_ = 'track').text
            }

    url = data[rand_Item].find('li', class_ = 'play')['data-url']

    return info, url


async def get_list_button_items(class_tag, object) -> list:
    page = requests.get(config.URL + str(random.randint(1, 10)))

    soup = BeautifulSoup(page.text, 'html.parser')

    data = list(item.text for item in soup.find_all('span', class_ = class_tag))

    unique_data_array = list()

    counter = config.QUANTITY_VARIANTS_ANSWER - 1

    while counter > 0:
        item = data[random.randint(0, len(data) - 1)]

        if re.findall(r'[a-zA-Z]', object.SONG_INFO[class_tag]):
            if (item not in unique_data_array) and (item != object.SONG_INFO[class_tag]) \
                and (re.findall(r'[a-zA-Z]', item)):
                    unique_data_array.append(item)
                    counter -= 1
        else:
            if (item not in unique_data_array) and (item != object.SONG_INFO[class_tag]) \
                and (re.findall(r'[а-яА-Я]', item)):
                    unique_data_array.append(item)
                    counter -= 1

    return unique_data_array
