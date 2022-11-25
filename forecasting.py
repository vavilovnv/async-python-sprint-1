# import logging
# import threading
# import subprocess
# import multiprocessing
import multiprocessing

from api_client import YandexWeatherAPI
from tasks import (
    DataCalculationTask,
    DataAggregationTask,
    DataAnalyzingTask,
)


def forecast_weather():
    """
    Анализ погодных условий по городам."""
    queue = multiprocessing.Queue()
    producer = DataCalculationTask(queue)
    consumer = DataAggregationTask(queue)

    producer.start()
    producer.join()

    consumer.start()
    consumer.join()


if __name__ == "__main__":
    forecast_weather()
