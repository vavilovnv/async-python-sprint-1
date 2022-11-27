import multiprocessing

from tasks import (
    DataCalculationTask,
    DataAggregationTask,
    DataAnalyzingTask,
)

from utils import logger


def forecast_weather():
    """
    Анализ погодных условий по городам."""
    queue = multiprocessing.Queue()
    producer = DataCalculationTask(queue)
    consumer = DataAggregationTask(queue)

    producer.start()
    logger.info(msg='Процесс producer запущен.')
    producer.join()

    consumer.start()
    logger.info(msg='Процесс consumer запущен.')
    consumer.join()

    logger.info(msg='Анализ данных...')
    DataAnalyzingTask().analyze()


if __name__ == "__main__":
    forecast_weather()
