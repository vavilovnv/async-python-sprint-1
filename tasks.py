import json
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process
from typing import List

from api_client import YandexWeatherAPI
from utils import (CITIES, GOOD_WHETHER, JSON_FILENAME, MAX_TIME, MIN_TIME,
                   STR_AVRG, STR_BEST_CITIES, STR_CITY, STR_HOURS, STR_RANK,
                   STR_TEMPERATURE, logger)


class DataFetchingTask:
    """Получение данных от YandexWeatherAPI."""

    @staticmethod
    def get_whether(city: str) -> dict:
        return YandexWeatherAPI().get_forecasting(city)


class DataCalculationTask(Process):
    """Обработка данных полученных от YandexWeatherAPI. Подсчет средней
    температуры и количества часов без осадков по городам. Если данные за
    день не содержат информации необходимой, такой день исключается из
    расчета."""

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    @staticmethod
    def day_calculation(hours: List[dict]) -> dict:
        temp, good_hours = [], 0
        for data in hours:
            if MIN_TIME <= int(data['hour']) <= MAX_TIME:
                temp.append(data['temp'])
                if data['condition'] in GOOD_WHETHER:
                    good_hours += 1
        average_temp = sum(temp) / len(temp)
        return {
            'average_temp': int(round(average_temp, 1)),
            'good_hours': good_hours
        }

    @staticmethod
    def city_calculation(city: str) -> dict:
        temp_data, good_hours_data = {}, {}
        temperature, good_hours = 0, 0
        forecast_data = DataFetchingTask().get_whether(city)
        for forecast in forecast_data['forecasts']:
            day, hours = forecast['date'], forecast['hours']
            try:
                day_data = DataCalculationTask.day_calculation(hours)
                temp_data[day] = day_data['average_temp']
                temperature += temp_data[day]
                good_hours_data[day] = day_data['good_hours']
                good_hours += good_hours_data[day]
            except ZeroDivisionError:
                logger.debug(
                    msg=f'Недостаточно данных по городу {city} за день {day}.'
                )
                continue
            temp_data[STR_AVRG] = round(temperature / len(temp_data), 1)
            good_hours_data[STR_AVRG] = (
                int(round(good_hours / len(good_hours_data), 0))
            )
        return {
            STR_CITY: city,
            STR_TEMPERATURE: temp_data,
            STR_HOURS: good_hours_data,
            STR_RANK: 0
        }

    def run(self) -> None:
        with ThreadPoolExecutor() as pool:
            data = pool.map(self.city_calculation, CITIES.keys())
            for city in data:
                self.queue.put(city)
                logger.info(msg=f'В очередь добавлен город {city}.')


class DataAggregationTask(Process):
    """Сведение полученных и обработанных данных о погоде по
    городам в один файл для анализа."""

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def run(self) -> None:
        data = []
        while True:
            if self.queue.empty():
                logger.info('Очередь очищена.')
                json_obj = json.dumps(data, indent=4, ensure_ascii=False)
                with open(JSON_FILENAME, 'w', encoding='utf-8') as f:
                    f.write(json_obj)
                logger.info(f'Сформирован файл {JSON_FILENAME}.')
                break
            city = self.queue.get()
            data.append(city)
            logger.info(msg=f'Из очереди получены данные по городу {city}.')


class DataAnalyzingTask:
    """Анализ данных о погоде, расчет рейтинга и обновление файла с данными.
    Определение города (или нескольких городов) с наилучшим рейтингом."""

    @staticmethod
    def analyze() -> None:
        with open('data.json''', 'r', encoding='utf-8') as f:
            data = json.load(f)
        cities = {
            i[STR_CITY]: (
                i[STR_TEMPERATURE][STR_AVRG],
                i[STR_HOURS][STR_AVRG]
            ) for i in data
        }
        ranks = {v: i for i, v in enumerate(sorted(set(cities.values())))}
        max_rank, ranked_cities = len(ranks) - 1, {}
        for city, score in cities.items():
            ranked_cities[city] = ranks[score]
        for data_city in data:
            city = data_city[STR_CITY]
            data_city[STR_RANK] = ranked_cities[city]
        data.sort(key=lambda x: x[STR_RANK], reverse=True)
        json_obj = json.dumps(data, indent=4, ensure_ascii=False)
        with open(JSON_FILENAME, 'w', encoding='utf-8') as f:
            f.write(json_obj)
        logger.info(f'Рассчитаны рейтинги городов в файле {JSON_FILENAME}.')
        best_cities = [i[STR_CITY] for i in data if i[STR_RANK] == max_rank]
        result_message = f'{STR_BEST_CITIES}: {",".join(best_cities)}'
        print(result_message)
        logger.info(msg=result_message)
