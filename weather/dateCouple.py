#import datetime to parse dates in ISO format
from datetime import datetime, timedelta, date
import dateutil.parser

import re

EARLIEST_DATE_STR = '1900-01-01T00:00:00Z'
ISO_TIME = 'T00:00:00Z'

#Check iso format for the date str
def fetch_date(str):
    if re.match(r'\A[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z\Z',str):
        return True
    return False

#Class to maintain the date couple organiced and do the error handling before creating the object
class DateCouple:
    origin = dateutil.parser.parse(EARLIEST_DATE_STR)
    today = dateutil.parser.parse(date.today().isoformat() + ISO_TIME)

    def __init__(self,start_date_str,end_date_str):
        if start_date_str == '' or end_date_str == '':
            raise Exception('Start and end date parameters must be defined')
        if not fetch_date(start_date_str) or not fetch_date(end_date_str):
            raise Exception('Start and end date parameters must be in ISO8601 format')
        self.start = dateutil.parser.parse(start_date_str)
        self.end = dateutil.parser.parse(end_date_str)
        if self.start > self.today:
            raise ValueError('Start date can\'t be a future date')
        if self.end > self.today:
            raise ValueError('End date can\'t be a future date')
        if self.start < self.origin:
            raise ValueError('Start date must be greater than '+EARLIEST_DATE_STR)
        if self.end < self.origin:
            raise ValueError('End date must be greater than '+EARLIEST_DATE_STR)
        if self.start > self.end:
            raise ValueError('End date must be greater than start date')

    #return an inclusive generator to iterate between the dates in the DateCouple
    def dateRange(self):
        for n in range(int ((self.end - self.start).days + 1)):
            yield self.start + timedelta(n)