from config import buffer_size
import uuid
from datetime import datetime as dt



class StateAudioClassifier:
    def __init__(self):
        self.request_limit = buffer_size
        self.request_data = dict()

#
    async def reg_new_request(self, file_url, reuse) -> dict:
        """
        Errors_list:
        0 - Отсутствует ошибка
        1 - Достигнут предел по количеству задач в работе одновременно.
        2 - Файл уже направлялся на распознавание ранее
        3 - Ошибка функции проверки нахождения задачи в работе
        """
        unique_id = str(uuid.uuid5(uuid.NAMESPACE_URL, str(file_url)))
        error = "3"
        error_description = None
        data = None

        # Проверить количество возможных запросов в буфере
        if len(self.request_data) > self.request_limit:
            error = "1"
            error_description = f"Reached buffer limit in {buffer_size} tasks"
        # Проверить есть ли в реестре
        else:
            if unique_id in self.request_data.keys():
                error = "2"
                error_description = "Order already proceeded to tasks list"
            else:
                error = "0"

        # добавить в реестр
        if error == "0":
            self.request_data[unique_id] = dict(
                    file_url=file_url,
                    start_date=dt.now(),
                    reuse=reuse,
                    state="new"
            )

            data = unique_id

        # отдать номер заявки
        return {
            "error": error,
            "error_description": error_description,
            "data": data
        }


State = StateAudioClassifier()
