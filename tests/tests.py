import json
import multiprocessing
import os
import pathlib as pl
import unittest

from tasks import (DataAggregationTask, DataAnalyzingTask,
                   DataCalculationTask, DataFetchingTask)
from utils import (JSON_FILENAME, STR_CITY, STR_TEMPERATURE, STR_HOURS,
                   STR_RANK)


class TasksTest(unittest.TestCase):

    QUEUE = multiprocessing.Queue()

    def test_data_fetching_task(self):
        response = DataFetchingTask().get_whether('MOSCOW')
        forecasts = response.get('forecasts')
        self.assertIsInstance(forecasts, list)
        self.assertGreater(len(forecasts), 0)
        forecast = forecasts[0]
        self.assertIsInstance(forecast, dict)
        self.assertEqual(forecast.get('date'), '2022-05-26')

    def test_data_calculation_task(self):
        queue = self.QUEUE
        task = DataCalculationTask(queue)
        task.run()
        self.assertTrue(not queue.empty())
        city = queue.get()
        self.assertIsInstance(city, dict)
        for key in (STR_CITY, STR_TEMPERATURE, STR_HOURS, STR_RANK):
            self.assertIn(key, city.keys())

    @staticmethod
    def delete_json_file(path):
        if path.is_file():
            os.remove(path)

    @staticmethod
    def assertIsFile(path):
        if not path.is_file():
            raise AssertionError(f'Файл не существует: {str(path)}')

    def test_data_aggregation_task(self):
        path = pl.Path(JSON_FILENAME).resolve()
        self.delete_json_file(path)
        queue = self.QUEUE
        produser = DataCalculationTask(queue)
        produser.run()
        consumer = DataAggregationTask(queue)
        consumer.run()
        self.assertTrue(queue.empty())
        self.assertIsFile(path)

    def test_data_analyzing_task(self):
        DataAnalyzingTask().analyze()
        with open('data.json''', 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        city = data[0]
        self.assertIn(STR_RANK, city.keys())
        self.assertGreater(city[STR_RANK], 0)


if __name__ == '__main__':
    unittest.main()
