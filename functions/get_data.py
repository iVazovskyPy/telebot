from loguru import logger


@logger.catch
def get_data(search_dict: dict, field: str):
    """
     Проходит по вложенным словарям/спискам и находит данные по искомому полю
    :param search_dict: dict()
    :param field: str()
    :return:
    """
    fields_found = []

    for key, value in search_dict.items():

        if key == field:
            fields_found.append(value)

        elif isinstance(value, dict):
            results = get_data(value, field)
            for result in results:
                fields_found.append(result)

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = get_data(item, field)
                    for another_result in more_results:
                        fields_found.append(another_result)

    return fields_found
