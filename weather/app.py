import time

# Import the framework
from flask import Flask,request,jsonify
from flask_restful import Resource, Api

import requests
import json

#import datetime to parse dates in ISO format
from datetime import datetime, date
import dateutil.parser

import redis

from dateCouple import DateCouple
from dataSet import DataSet

# Create an instance of Flask
app = Flask(__name__)

# Create the API
api = Api(app)

REDIS_PORT = 6379
TEMPERATURE_SERVICE = 'http://temperature:8000/?at='
WINDSPEEDS_SERVICE = 'http://windspeed:8080/?at='
TEMPERATURES = "temperatures"
NORTH_SPEEDS = 'northSpeeds'
WEST_SPEEDS = 'westSpeeds'

cache = redis.Redis(host='redis', port=REDIS_PORT)


#loop between date range inclusive
def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days + 1)):
        yield start_date + timedelta(n)

# calls the specific service for all the dates in the range and retrieves the data
def start_service(dateCouple,type):
    data = []
    for single_date in dateCouple.dateRange():
        #max number of atempts
        retries = 5
        caching = True
        while caching:
            try:
                dataSet = createDataSet(single_date,type)
                caching = False
            except redis.exceptions.ConnectionError as exc:
                if retries == 0:
                    #trigger exception if not able to connect to redis after 5 atempts
                    raise exc
                retries -= 1
                time.sleep(0.5)
            except Exception as e:
                ermsg = "Unexpected error: " + str(e)
                return jsonify({'error':ermsg})
            data.append(dataSet.getData())
    return jsonify(data)

#creates a DataSet from cached data and calls the backing services only when needed
def createDataSet(single_date,type):
    iso_date = single_date.isoformat().replace('+00:00','Z')
    single_date_str = single_date.strftime("%y-%m-%d")
    cached_temps = checkCache(single_date_str,'temps')
    cached_speeds = checkCache(single_date_str,'speeds')
    params = {'date':iso_date}
    if (type == 'temps' or type == 'weather') and cached_temps:
        #reading temps from cache
        params['temp'] = json.loads(cache.hget(TEMPERATURES,single_date_str))
    elif (type == 'temps' or type == 'weather') and not cached_temps:
        #calling the backing service and caching values for that date
        url = TEMPERATURE_SERVICE + iso_date
        response = requests.get(url)
        params['temp'] = response.json().get('temp')
        cache.hsetnx(TEMPERATURES,single_date_str,params.get('temp'))
    if (type == 'speeds' or type == 'weather') and cached_speeds:
        #reading speeds from cache
        params['north'] =  json.loads(cache.hget(NORTH_SPEEDS,single_date_str))
        params['west'] =  json.loads(cache.hget(WEST_SPEEDS,single_date_str))
    elif (type == 'speeds' or type == 'weather') and not cached_speeds:
        #calling the backing service and caching values for that date
        url = WINDSPEEDS_SERVICE + iso_date
        response = requests.get(url)
        params['north'] = response.json().get('north')
        params['west'] = response.json().get('west')
        cache.hsetnx(NORTH_SPEEDS,single_date_str,params.get('north'))
        cache.hsetnx(WEST_SPEEDS,single_date_str,params.get('west'))
    return DataSet(type,params)

#checks if the service type was already cached for that date
def checkCache(date_str,type):
    if type == 'temps' and cache.hexists(TEMPERATURES,date_str):
        return True
    if type == 'speeds' and cache.hexists(NORTH_SPEEDS,date_str):
        return True
    return False

# creates a DateCouple and start the service if there's no errors
def start_request(args, type):
    try:
        dateCouple = DateCouple(args.get('start',''),args.get('end',''))
        return start_service(dateCouple,type)
    except Exception as e:
        return jsonify({'error':str(e)})

class Temperatures(Resource):
    def get(self):
        return start_request(request.args,'temps')

class Speeds(Resource):
    def get(self):
        return start_request(request.args,'speeds')

class Weather(Resource):
    def get(self):
        return start_request(request.args,'weather')

api.add_resource(Temperatures, '/temperatures')
api.add_resource(Speeds, '/speeds')
api.add_resource(Weather, '/weather')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)