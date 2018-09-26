import unittest
import logging
import sys
from dateCouple import DateCouple as dc
from dataSet import DataSet as ds

EARLIEST_DATE_STR = '1900-01-01T00:00:00Z'

class TestDateCouple(unittest.TestCase):
    def test_empty_date_str(self):
        log = logging.getLogger("TestDateCouple")
        log.debug("\n%s","Testing invalid or empty parameters for data couple")
        end_date_str = ""
        start_date_str = "2018-08-01T00:00:00Z"
        with self.assertRaises(Exception) as context:
            dc(start_date_str,end_date_str)
        self.assertTrue('Start and end date parameters must be defined' in str(context.exception))
    def test_invalid_format_date_str(self):
        log = logging.getLogger("TestDateCouple")
        log.debug("\n%s","Testing invalid ISO format date parameters for data couple")
        end_date_str = "2018/08/01 00:00:00Z"
        start_date_str = "2018-08-01T00:00:00Z"
        with self.assertRaises(Exception) as context:
            dc(start_date_str,end_date_str)
        self.assertTrue('Start and end date parameters must be in ISO8601 format' in str(context.exception))
    def test_future_start_date_str(self):
        log = logging.getLogger("TestDateCouple")
        log.debug("\n%s","Testing future start date for data couple")
        start_date_str = "2999-01-01T00:00:00Z"
        end_date_str = "2018-08-01T00:00:00Z"
        with self.assertRaises(ValueError) as context:
            dc(start_date_str,end_date_str)
        self.assertTrue('Start date can\'t be a future date' in str(context.exception))
    def test_future_end_date_str(self):
        log = logging.getLogger("TestDateCouple")
        log.debug("\n%s","Testing future end date for data couple")
        end_date_str = "2999-01-01T00:00:00Z"
        start_date_str = "2018-08-01T00:00:00Z"
        with self.assertRaises(ValueError) as context:
            dc(start_date_str,end_date_str)
        self.assertTrue('End date can\'t be a future date' in str(context.exception))
    def test_oldest_start_date_str(self):
        log = logging.getLogger("TestDateCouple")
        log.debug("\n%s","Testing oldest start date for data couple")
        end_date_str = "2018-08-01T00:00:00Z"
        start_date_str = "1899-01-01T00:00:00Z"
        with self.assertRaises(ValueError) as context:
            dc(start_date_str,end_date_str)
        self.assertTrue(('Start date must be greater than ' + EARLIEST_DATE_STR) in str(context.exception))
    def test_oldest_end_date_str(self):
        log = logging.getLogger("TestDateCouple")
        log.debug("\n%s","Testing oldest end date for data couple")
        start_date_str = "2018-08-01T00:00:00Z"
        end_date_str = "1899-01-01T00:00:00Z"
        with self.assertRaises(ValueError) as context:
            dc(start_date_str,end_date_str)
        self.assertTrue(('End date must be greater than ' + EARLIEST_DATE_STR) in str(context.exception))
    def test_start_date_greater_than_end_date_str(self):
        log = logging.getLogger("TestDateCouple")
        log.debug("\n%s","Testing end date is greater than start date for data couple")
        start_date_str = "2018-08-10T00:00:00Z"
        end_date_str = "2018-08-01T00:00:00Z"
        with self.assertRaises(ValueError) as context:
            dc(start_date_str,end_date_str)
        self.assertTrue('End date must be greater than start date' in str(context.exception))

class TestDataSet(unittest.TestCase):
    def test_empty_date(self):
        log = logging.getLogger("TestDataSet")
        log.debug("\n%s","Testing invalid or missing type on DataSet")
        type = ""
        params = {}
        with self.assertRaises(ValueError) as context:
            ds(type,params)
        self.assertTrue('unknown type in constructor' in str(context.exception))
    def test_empty_temp_param(self):
        log = logging.getLogger("TestDataSet")
        log.debug("\n%s","Testing invalid or missing temp param on DataSet")
        type = "temps"
        params = {'temp':''}
        with self.assertRaises(ValueError) as context:
            ds(type,params)
        self.assertTrue('invalid or missing temp parameter' in str(context.exception))
    def test_invalid_west_param(self):
        log = logging.getLogger("TestDataSet")
        log.debug("\n%s","Testing invalid or missing west param on DataSet")
        type = "speeds"
        params = {'north':12.9,'west':'sadsdas'}
        with self.assertRaises(ValueError) as context:
            ds(type,params)
        self.assertTrue('invalid or missing west parameter' in str(context.exception))
    def test_invalid_north_param(self):
        log = logging.getLogger("TestDataSet")
        log.debug("\n%s","Testing invalid or missing north param on DataSet")
        type = "speeds"
        params = {'north':''}
        with self.assertRaises(ValueError) as context:
            ds(type,params)
        self.assertTrue('invalid or missing north parameter' in str(context.exception))
    def test_get_data_from_data_set(self):
        log = logging.getLogger("TestDataSet")
        log.debug("\n%s","Testing DataSet getData")
        type = "weather"
        params = {'temp': 8.0, 'north':12.1, 'west':-2.3, 'date':'2018-08-01T00:00:00Z' }
        dataSet = ds(type,params)
        self.assertEqual(params,dataSet.getData())

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("TestDateCouple").setLevel( logging.DEBUG )
    logging.getLogger("TestDataSet").setLevel( logging.DEBUG )
    logging.getLogger("TestApp").setLevel( logging.DEBUG )
    unittest.main()