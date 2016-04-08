import json
import pymongo
from pymongo import MongoClient

client = MongoClient('mongodb://107.170.244.164/', 27017)

db = client.mars_db
game_coll = db.game_data
sensor_coll = db.sensor_data


# Inserts the json data into the sensor_data collection
# Returns the inserted_id
def game_insert(json_data):
    result = game_coll.insert_one(json_data)
    return result.inserted_id


# Gets the data based on the json query
def game_get(json_query):
    return game_coll.find(json_query)


# Returns an array of all of the data in the sensor_data
# collection
def game_get_all():
    return game_coll.find()


# Gets the records where all of the readings are greater than
# the specified readings
#
# Give the radiation value first, then the temperature value
# then the flare value
def game_get_threshold(rad, temp, flare):
    new_rad = "$gt: " + rad
    new_temp = "$gt: " + temp

    return game_coll.find({"readings.radiation": new_rad,
        "readings.temperature": new_temp,
        "readings.solarFlare": flare})


def game_reset():
    game_coll.drop()


# Inserts the json data into the sensor_data collection
# Returns the inserted_id
def sensor_insert(json_data):
    result = sensor_coll.insert_one(json_data)
    return result.inserted_id


# Gets the data based on the json query
def sensor_get(json_query):
    return sensor_coll.find(json_query)


# Returns an array of all of the data in the sensor_data
# collection
def sensor_get_all():
    return sensor_coll.find()


# Gets the records where all of the readings are greater than
# the specified readings
#
# Give the radiation value first, then the temperature value
# then the flare value
def sensor_get_threshold(rad, temp, flare):
    new_rad = "$gt: " + rad
    new_temp = "$gt: " + temp

    return sensor_coll.find({"readings.radiation": new_rad,
        "readings.temperature": new_temp,
        "readings.solarFlare": flare})


def sensor_reset():
    sensor_coll.drop()

