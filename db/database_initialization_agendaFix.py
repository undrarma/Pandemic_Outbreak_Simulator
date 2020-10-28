import random
import utils
import numpy
from pprint import pprint

from pymongo import MongoClient
from secrets import MONGO_CLUSTER

# Parameters
AGENDA_SIZE = 100

def populateLocation(client):
    db = client.simulator
    locationsColl = db.locations

    for location in utils.locations:
        locationArr = []
        for x in range(random.randint(10, 50)):
            locationArr.append(random.sample(range(10000000), 1)[0])
        locationJson = {
            "activity": location,
            "locations": locationArr
        }
        locationsColl.insert_one(locationJson)

def populateAgenda(client, number_of_agendas):
    db = client.simulator
    agendas = db.agenda

    activities = dict()
    activities["under_three_years_activities"] = "home"
    activities["three_to_six_years_activities"] = "daycare,home"
    activities["six_to_twelve_years_activities"] = "school,home,sport"
    activities["twelve_to_eighteen_years_activities"] = "highschool,home,sport,recreational places,work"
    activities["college_students_activities"] = "college,dormitory,recreational places,sport"
    activities["adults_activities"] = "work,home,recreational places,sport"
    activities["over_sixty_years_activities"] = "home,recreational places"

    allLocationsDict = dict()
    for activity in utils.locations:
        allLocationsDict[activity] = list(db.locations.find({"activity": activity}))[0]

    for i in range(number_of_agendas):
        locationsDict = dict.fromkeys(utils.locations, [])
        for activity in utils.locations:
            locationsDict[activity] = random.choice(allLocationsDict[activity]['locations'])

        schedule = []
        activity_pool = []
        agenda_type = random.choices(utils.AGENDA_TYPES, weights=[.2, .1, .1, .1, .05, .45, .1])[0]

        if agenda_type == "under_three_years_activities":
            for j in range(utils.DAY_HOURS):
                schedule.append({"activity_id" : "home", "location_id" : locationsDict['home'], "time" : "{:02d}:00".format(j)})
            continue
        else:
            activity_pool = activities[agenda_type]


        hour_sleep = random.choices(range(24), weights=[.15, .1, .05, .01, .01, .01, .01, .01, .01, .01, .01, .01, .01, .01, .01, .01, .01, .01, .01, .01, .01, .12, .2, .2])[0]
        hours_sleeping = random.choices([4, 5, 6, 7, 8, 9, 10], weights=[.05, .1, .2, .25, .25, .1, .05])[0]
        j = hour_sleep
        while True:
            if j == (hour_sleep + hours_sleeping) % 24:
                break
            schedule.append({"activity_id" : "home", "location_id" : locationsDict['home'], "time" : "{:02d}:00".format(j)})
            j = (j + 1) % 24

        hours_main_activity = random.choices([4, 5, 6, 7, 8, 9, 10], weights=[.15, .05, .1, .05, .5, .1, .05])[0]
        hour_main_activity = (hour_sleep + hours_sleeping) % 24
        main_activity = activity_pool.split(',')[0]
        j = hour_main_activity
        while True:
            if j == (hour_main_activity + hours_main_activity) % 24:
                break
            schedule.append({"activity_id" : main_activity, "location_id" : locationsDict[main_activity], "time" : "{:02d}:00".format(j)})
            j = (j + 1) % 24

        j = hour_main_activity + hours_main_activity
        while len(schedule) < 24:
            currentActivity = random.choice(activity_pool.split(',')[1:])
            schedule.append({"activity_id" : currentActivity, "location_id" : locationsDict[currentActivity], "time" : "{:02d}:00".format(j)})
            j = (j + 1) % 24

        agenda_json = {
            "agenda_type": agenda_type,
            "schedule": schedule
        }

        agendas.insert_one(agenda_json)

def initializeGlobalVariables(client):
    db = client.simulator
    globalVariables = db.global_variables

    simulation_counter = {
        "attribute_name": "simulation_counter",
        "value" : 0
    }
    globalVariables.insert_one(simulation_counter)

    user_sim = db.user_simulation
    user_sim.insert_one({"user_id": -1})

def main():
    client = MongoClient(MONGO_CLUSTER)
    print("Initialization started")
    # populateLocation(client)
    # initializeGlobalVariables(client)
    populateAgenda(client, AGENDA_SIZE)

if __name__ == "__main__":
    main()
