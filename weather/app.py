
import time

# Import the framework
from flask import Flask,request,jsonify
from flask_restful import Resource, Api

import requests
import json

#import datetime to parse dates in ISO format
from datetime import datetime, timedelta, date
import dateutil.parser

import redis

# Create an instance of Flask
app = Flask(__name__)

# Create the API
api = Api(app)

cache = redis.Redis(host='redis', port=6379)
temperatureList = "temperatures"
northSpeedList = 'northSpeeds'
westSpeedList = 'westSpeeds'

#loop between date range inclusive
def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days + 1)):
        yield start_date + timedelta(n)

# calls the specific service for all the dates in the range and retrieves the data
def get_data(start_date,end_date,type):
    data = []
    for single_date in daterange(start_date, end_date):
        # #max number of atempts
        retries = 5
        #fix for date format to RFC3339
        iso_date = single_date.isoformat().replace('+00:00','Z')
        while True:
            try:
                ready = False
                single_date_str = single_date.strftime("%y-%m-%d")
                cached_temps = cache.hexists(temperatureList,single_date_str)
                cached_speeds = cache.hexists(northSpeedList,single_date_str)
                if cached_temps and (type == 'temps' or type == 'both'):
                    #reading temp from cache
                    temp = json.loads(cache.hget(temperatureList,single_date_str))
                    ready = True
                elif not cached_temps and (type == 'temps' or type == 'both'):
                    #calling the backing service and caching values for that date
                    service = 'http://temperature:8000/?at='
                    url = service + iso_date
                    response = requests.get(url)
                    temp = response.json().get('temp')
                    cache.hsetnx(temperatureList,single_date_str,temp)
                    ready = True
                if cached_speeds and (type == 'speeds' or type == 'both'):
                    #reading speeds from cache
                    north = json.loads(cache.hget(northSpeedList,single_date_str))
                    west = json.loads(cache.hget(westSpeedList,single_date_str))
                    ready = True
                elif not cached_speeds and (type == 'speeds' or type == 'both'):
                    #calling the backing service and caching values for that date
                    service = 'http://windspeed:8080/?at='
                    url = service + iso_date
                    response = requests.get(url)
                    north = response.json().get('north')
                    west = response.json().get('west')
                    cache.hsetnx(northSpeedList,single_date_str,north)
                    cache.hsetnx(westSpeedList,single_date_str,west)
                    ready = True
                if ready:
                    break
            except redis.exceptions.ConnectionError as exc:
                if retries == 0:
                    #trigger exception if not able to connect to redis after 5 atempts
                    raise exc
                retries -= 1
                time.sleep(0.5)
            except Exception as e:
                ermsg = "Unexpected error: " + str(e)
                return jsonify({'error':ermsg})
        if type == 'temps':
            data.append({'temp':temp,'date':iso_date})
        elif type == 'speeds':
            data.append({'north':north,'west':west,'date':iso_date})
        else:
            data.append({'north':north,'west':west,'temp':temp,'date':iso_date})
    return jsonify(data)

# checks start_date and end_date parameters before calling get_data to prevent errors with 
def start_service(start_date_str, end_date_str, type):
    #checking start_date and end_date are defined
    if start_date_str == '' or end_date_str == '':
        return jsonify({'error':'missing parameter in request.(start & end parameters must be defined in the request)'})
    
    today_date_str = date.today().isoformat() + 'T00:00:00Z'
    smallest_date_str = "1900-01-01T00:00:00Z"
    
    try:
        smallest_date = dateutil.parser.parse(smallest_date_str)
        start_date = dateutil.parser.parse(start_date_str)
        end_date = dateutil.parser.parse(end_date_str)
        today_date = dateutil.parser.parse(today_date_str)
    except Exception as e:
        ermsg = "Error while parsing dates: " + str(e)
        return jsonify({'error':ermsg})
    
    #checking start_date is greater than the smallest date
    if smallest_date > start_date:
        return jsonify({'error':'start date is older than jan 01 1900'})
    #checking end_date is greater than the smallest date
    if smallest_date > end_date:
        return jsonify({'error':'end date is older than jan 01 1900'})
    #checking start_date occurs before today
    if start_date > today_date:
        return jsonify({'error':'start date is in the future'})
    #checking end_date occurs before today
    if end_date > today_date:
        return jsonify({'error':'end date is in the future'})
    #checking end_date greater than start_date
    if end_date < start_date:
        return jsonify({'error':'start date must be smaller than the end date'})
    return get_data(start_date,end_date,type)

class Temperatures(Resource):
    def get(self):
        start_date_str = request.args.get('start','')
        end_date_str = request.args.get('end','')
        return start_service(start_date_str,end_date_str,'temps')

class Speeds(Resource):
    def get(self):
        start_date_str = request.args.get('start','')
        end_date_str = request.args.get('end','')
        return start_service(start_date_str,end_date_str,'speeds')

class Weather(Resource):
    def get(self):
        start_date_str = request.args.get('start','')
        end_date_str = request.args.get('end','')
        return start_service(start_date_str,end_date_str,'both')

api.add_resource(Temperatures, '/temperatures')
api.add_resource(Speeds, '/speeds')
api.add_resource(Weather, '/weather')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)