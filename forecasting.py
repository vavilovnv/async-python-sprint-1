# import logging
# import threading
# import subprocess
# import multiprocessing
import multiprocessing

from api_client import YandexWeatherAPI
from tasks import (
    DataFetchingTask,
    DataCalculationTask,
    DataAggregationTask,
    DataAnalyzingTask,
)
from utils import CITIES


def forecast_weather():
    """
    Анализ погодных условий по городам
    """
    queue = multiprocessing.Queue()
    producer = DataCalculationTask(queue)
    consumer = DataAggregationTask(queue)


if __name__ == "__main__":
    forecast_weather()
