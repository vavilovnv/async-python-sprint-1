import multiprocessing

from tasks import (
    DataCalculationTask,
    DataAggregationTask,
    DataAnalyzingTask,
)

from utils import get_logger


logger = get_logger()


def forecast_weather():
    """
    Анализ погодных условий по городам."""
    queue = multiprocessing.Queue()
    producer = DataCalculationTask(queue)
    consumer = DataAggregationTask(queue)

    producer.start()
    logger.info(msg='Producer process started.')
    producer.join()

    consumer.start()
    logger.info(msg='Consumer process started.')
    consumer.join()

    logger.info(msg='Data analyze...')
    DataAnalyzingTask().analyze()


if __name__ == "__main__":
    forecast_weather()
