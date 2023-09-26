from loguru import logger
from functions.get_data import get_data
from rapidapi_key import rapidapi_key
import requests
import re
import json
from forex_python.converter import CurrencyRates


@logger.catch
def get_hotels(inf, loc: str, rev=None):
    """
    Возвращает список отелей и их параметров
    :param inf: str()
    :param loc: str()
    :param rev: bool
    :return:
    """
    destination_id_list = list()

    for i in inf['suggestions']:
        if i['group'] == 'CITY_GROUP':
            destination_id_list.append(get_data(i, 'destinationId'))

    destination_id_list = destination_id_list[0]
    response_groups = list()

    url = "https://hotels4.p.rapidapi.com/properties/list"

    for i_id in destination_id_list:
        querystring = {"adults1": "1", "pageNumber": "1", "destinationId": i_id, "pageSize": "25",
                       "checkOut": "2020-01-15",
                       "checkIn": "2020-01-08", "sortOrder": "PRICE", "locale": loc, "currency": "USD"}

        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': "hotels4.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        response = json.loads(response.text)
        response_groups.append(response)

    names_dirty_list = get_data(response_groups[0], 'name')
    names = [i_elem for i_elem in names_dirty_list if isinstance(i_elem, str)]

    distances_dirty_list = get_data(response_groups[0], 'landmarks')
    distances_clear_list = list()
    pattern = str()
    if loc == 'en_US':
        pattern = r' (miles|mile)'
    elif loc == 'ru_RU':
        pattern = r' км'

    center = str()
    if loc == 'en_US':
        center = 'City center'
    elif loc == 'ru_RU':
        center = 'Центр города'
    for i_list in distances_dirty_list:
        for i_dict in i_list:
            if isinstance(i_dict, dict) and i_dict['label'] == center:
                distance = i_dict['distance']
                distance = re.sub(pattern, '', distance)
                if ',' in distance:
                    distance = re.sub(",", '.', distance)
                distances_clear_list.append(float(distance))

    prices = get_data(response_groups[0], 'exactCurrent')

    result_data = [[names[i_index], prices[i_index], distances_clear_list[i_index]] for i_index in range(len(names))]

    lowprice_result = sorted(result_data, key=lambda k: k[1])

    if rev:
        lowprice_result = list(reversed(lowprice_result))

    res = str()
    for i_list in lowprice_result:
        hotel, price, distance = i_list
        if loc == 'en_US':
            res += f'{hotel}, Price - {price}$, Distance from downtown - {distance} ml\n'
        elif loc == 'ru_RU':
            c = CurrencyRates()
            rate = c.get_rate('USD', 'RUB')
            res += f'{hotel}, Цена - {round(price*rate, 2)} руб., Удаленность от центра - {distance} км\n'
        res += '\n'

    return res
