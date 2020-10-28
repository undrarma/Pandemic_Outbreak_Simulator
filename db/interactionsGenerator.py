# import random
import utils

from pymongo import MongoClient, WriteConcern, ReadPreference, InsertOne, UpdateOne
from datetime import datetime
from datetime import timedelta
from secrets import MONGO_CLUSTER
from itertools import combinations
import json
from bson import json_util
from collections import Counter
# import sys
# import os
# import psutil
# import elasticache_auto_discovery
# from pymemcache.client.hash import HashClient

# Parameters
numDays = 100
start = 0
end = 0

def addInteraction(interactionsArray, timestamp, bulk_write, populationStatuses):
    # db = client.simulator
    # popullation = db['popullation_{}'.format(simulation_id)]
    personsCombinations = list(combinations(interactionsArray, 2))
    for combination in personsCombinations:
        if combination[0][1] == "infectious":
            populationStatuses[combination[0][0]] = "infected"
            statusQuery = {"person_id": combination[0][0]}
            statusValues = {'$set': {'infection_status': 'infected'}}
            bulk_write.append(UpdateOne(statusQuery, statusValues))
        elif combination[1][1] == "infectious":
            populationStatuses[combination[1][0]] = "infected"
            statusQuery = {'person_id': combination[1][0]}
            statusValues = {'$set': {'infection_status': 'infected'}}
            bulk_write.append(UpdateOne(statusQuery, statusValues))
        else:
            interactionQuery = {"person_id": combination[0][0]}
            newInteraction = {"$set": {"interactions": {"person_id": combination[1][0], "timestamp": timestamp}}}
            bulk_write.append(UpdateOne(interactionQuery, newInteraction))
            interactionQuery = {"person_id": combination[1][0]}
            newInteraction = {"$set": {"interactions": {"person_id": combination[0], "timestamp": timestamp}}}
            bulk_write.append(UpdateOne(interactionQuery, newInteraction))

def reviewLocations(popullation, day, allLocationsDict, populationStatuses, populationInfo):

    # # Locations Dictionary
    # allLocationsDict = dict()
    # for activity in utils.locations:
    #     allLocationsDict[activity] = list(db.locations.find({"activity": activity}))[0]

    # # Statuses Dictionary
    # populationStatuses = dict()
    # for person in list(popullation.find({}, {'_id': 0, 'person_id': 1, 'infection_status': 1})):
    #     populationStatuses[person['person_id']] = person['infection_status']

    bulk_write = []
    for hour in range(24):
        # print(hour)
        for activityKey in allLocationsDict.keys():
            for locationID in allLocationsDict[activityKey]['locations']:
                # myquery = [{"$match":{"agenda.0.schedule."+str(hour)+".location_id": locationID}}] #locationID}}]
                # person = list(popullation.aggregate(myquery))[0]
                personsArr = populationInfo['agenda.0.schedule.'+"{:02d}".format(hour)+'.location_id.'+str(locationID)]
                # myquery = {"agenda.0.schedule." + str(hour) + ".location_id": locationID}
                # personsArr = [[id["person_id"], id["infection_status"]] for id in list(popullation.find(myquery))]
                if len(personsArr) > 1:
                    addInteraction(personsArr, datetime.now().date() + timedelta(days=day), bulk_write, populationStatuses)
    # result = popullation.bulk_write(bulk_write)

    return populationStatuses

def fillMemcacheDict(population, allLocationsDict):
    # # elasticache settings
    # elasticache_config_endpoint = "simulationcluster.gipshq.cfg.use2.cache.amazonaws.com:11211"
    # nodes = elasticache_auto_discovery.discover(elasticache_config_endpoint)
    # nodes = map(lambda x: (x[1], x[2]), nodes)
    # memcache_client = HashClient(nodes)

    jsonArr = []
    for person in list(population.find({}, {'_id': 0, 'person_id': 1, 'infection_status': 1, 'agenda': 1})):
        jsonArr.append(person)

    jsonStr = json_util.dumps(jsonArr)
    jsonObj = json.loads(jsonStr)

    populationInfo = dict()
    for hour in range(24):
        # print("{:02d}".format(hour))
        personArr = []
        # print(hour)
        for activityKey in allLocationsDict.keys():
            for locationID in allLocationsDict[activityKey]['locations']:
                populationInfo['agenda.0.schedule.'+"{:02d}".format(hour)+'.location_id.'+str(locationID)] = [[id["person_id"], id["infection_status"]] for id in jsonObj if id["agenda"][0]["schedule"][int("{:02d}".format(hour))]["location_id"] == locationID]
                # personArr.append([[id["person_id"], id["infection_status"]] for id in jsonObj if id["agenda"][0]["schedule"][int("{:02d}".format(hour))]["location_id"] == locationID])
    # if populationPerson['agenda'][0]['schedule']['location_id'] == 6806298

    # print(sys.getsizeof(populationInfo))

    return populationInfo

def main():
    client = MongoClient(MONGO_CLUSTER)
    db = client.simulator
    popullation = db['popullation_{}'.format(50)]
    print("Initialization started")

    # Locations Dictionary
    allLocationsDict = dict()
    for activity in utils.locations:
        allLocationsDict[activity] = list(db.locations.find({"activity": activity}))[0]

    populationInfo = fillMemcacheDict(popullation, allLocationsDict)
    # print(populationInfo)

    # Statuses Dictionary
    populationStatuses = dict()
    for person in list(popullation.find({}, {'_id': 0, 'person_id': 1, 'infection_status': 1})):
        populationStatuses[person['person_id']] = person['infection_status']

    statistics_per_day = []
    for day in range(0, 100):
        statuses = list(populationStatuses.values())
        statistics_per_day.append({'day': day, 'groups': dict(Counter(statuses))})
        populationStatuses = reviewLocations(popullation, day, allLocationsDict, populationStatuses, populationInfo)
        # print(statistics_per_day)

    # for i in range(numDays):
    #     interactionsGen()

if __name__ == "__main__":
    main()
