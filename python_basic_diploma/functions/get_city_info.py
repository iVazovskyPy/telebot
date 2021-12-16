from loguru import logger
import requests
from rapidapi_key import rapidapi_key
import json


@logger.catch
def get_city_info(ct: str, loc: str):
    """
    Получает данные о городе с сервера
    :param ct: str()
    :param loc: str()
    :return:
    """
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": ct, "locale": loc, "currency": "USD"}

    headers = {
        'x-rapidapi-key': rapidapi_key,
        'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return json.loads(response.text)