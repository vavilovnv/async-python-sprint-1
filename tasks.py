from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process

from api_client import YandexWeatherAPI
from utils import CITIES


class DataFetchingTask:

    @staticmethod
    def get_whether(city):
        return YandexWeatherAPI().get_forecasting(city)


class DataCalculationTask(Process):

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    @staticmethod
    def day_calculation(hours):
        temp = []
        for hour in hours:
            temp.append(hour.temp)

    @staticmethod
    def city_calculation(city):
        forecast_data = DataFetchingTask().get_whether(city)
        for data in forecast_data.forecast:
            result = DataCalculationTask.day_calculation(data.hours)


    def run(self) -> None:
        with ThreadPoolExecutor() as pool:
            data = pool.map(self.calculate, CITIES.keys())
            for city in data:
                self.queue.put(city)


class DataAggregationTask(Process):
    pass


class DataAnalyzingTask:
    pass


