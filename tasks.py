import json

from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process

from api_client import YandexWeatherAPI
from utils import (CITIES, GOOD_WHETHER, MIN_TIME, MAX_TIME, STR_HOURS,
                   STR_TEMPERATURE)


class DataFetchingTask:

    @staticmethod
    def get_whether(city):
        return YandexWeatherAPI().get_forecasting(city)


class DataCalculationTask(Process):

    DAY_HOURS = MAX_TIME - MIN_TIME

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    @staticmethod
    def day_calculation(hours):
        temp, good_hours = [], 0
        for data in hours:
            if MIN_TIME <= int(data['hour']) <= MAX_TIME:
                temp.append(data['temp'])
                if data['condition'] in GOOD_WHETHER:
                    good_hours += 1
        average_temp = sum(temp) / DataCalculationTask.DAY_HOURS
        return {
            'average_temp': average_temp,
            'good_hours': good_hours
        }

    @staticmethod
    def city_calculation(city):
        temp_data, good_hours_data = [], []
        forecast_data = DataFetchingTask().get_whether(city)
        for forecast in forecast_data['forecasts']:
            day_data = DataCalculationTask.day_calculation(forecast['hours'])
            temp_data.append(day_data['average_temp'])
            good_hours_data.append(day_data['good_hours'])
        average_temp = round(sum(temp_data) / len(temp_data), 1)
        average_good_hours = int(round(sum(good_hours_data) / len(good_hours_data), 0))
        return {
            city: {
                STR_TEMPERATURE: average_temp,
                STR_HOURS: average_good_hours
            }
        }

    def run(self) -> None:
        with ThreadPoolExecutor() as pool:
            data = pool.map(self.city_calculation, CITIES.keys())
            for city in data:
                self.queue.put(city)


class DataAggregationTask(Process):

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def run(self) -> None:
        data = []
        while True:
            if self.queue.empty():
                json_obj = json.dumps(data, indent=4, ensure_ascii=False)
                with open("data.json", "w", encoding='utf-8') as f:
                    f.write(json_obj)
                break
            data.append(self.queue.get())


class DataAnalyzingTask:
    pass
