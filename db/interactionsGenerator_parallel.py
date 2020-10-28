import utils

from pymongo import MongoClient, WriteConcern, ReadPreference, InsertOne, UpdateOne
from datetime import datetime
from datetime import timedelta
from secrets import MONGO_CLUSTER
from itertools import combinations
from collections import Counter

import multiprocessing as mp



# Parameters
numDays = 100
start = 0
end = 0
NUM_OF_PROCESSES = 8

class ParallelQuery(object):

    # This is the task of each sub-process
    def executeQuery(self, queries, conn):
        # Establish connection with the database
        client = MongoClient(MONGO_CLUSTER)
        db = client.simulator
        popullation = db['popullation_{}'.format(50)]

        # Initialize some variables
        result = []
        dic = {}
        i=0

        # Create a dictionary with all the queries that will be run
        for query in queries:
            dic["query"+str(i)] = query
            i+=1
            # Query one by one
            # personsArr = [[id["person_id"], id["infection_status"]] for id in list(popullation.find(query, {"person_id":1, "infection_status":2, "_id": 0}))]
            # #personsArr = [[id["person_id"], id["infection_status"]] for id in list(popullation.find(query))]
            # if len(personsArr) > 1:
            #     result.append((personsArr))

        # Bulk query using $facet
        myquery = [{ '$facet': dic}]
        person = list(popullation.aggregate(myquery))[0]
        for j in range(0,i):
            personsArr = [[id["person_id"], id["infection_status"]] for id in list(person["query"+str(j)])]
            if len(personsArr) > 1:
                 result.append((personsArr))
        conn.send(result)
        conn.close()

    def addInteraction(self, interactionsArray, timestamp, bulk_write, populationStatuses):
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


    def reviewLocations(self, popullation, day, allLocationsDict, populationStatuses):
        num_workers = mp.cpu_count()
        client = MongoClient(MONGO_CLUSTER)
        pool = mp.Pool(num_workers)
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
            print(hour)

            queries = []
            processes = []
            parent_connections = []

            for activityKey in allLocationsDict.keys():

                i = 0
                for locationID in allLocationsDict[activityKey]['locations']:
                    #myquery = {"agenda.0.schedule." + str(hour) + ".location_id": locationID}
                    myquery = [ {'$project':{'_id':0,'person_id':1,'infection_status':1, 'agenda':1}},
                                {'$match':{"agenda.0.schedule." + str(hour) + ".location_id": locationID}},
                                {'$project':{'_id':0,'person_id':1,'infection_status':1}},
                                ]
                    # Create a list of all the queries to be run
                    queries.append(myquery)
                    i += 1

            queries_num = len(queries)
            start = 0

            # Create processes to run in parallel
            # Each process will execute a set of queries
            for p in range(0,NUM_OF_PROCESSES):
                # create a pipe for communication
                parent_conn, child_conn = mp.Pipe()
                parent_connections.append(parent_conn)
                end = start + int(queries_num/NUM_OF_PROCESSES)

                # Assign a job to each process
                if p != NUM_OF_PROCESSES-1:
                    process = mp.Process(target=self.executeQuery, args=(queries[start:end],  child_conn,))
                else:
                    process = mp.Process(target=self.executeQuery, args=(queries[start:],  child_conn,))
                processes.append(process)
                start += int(queries_num/NUM_OF_PROCESSES)

            # Launch all the processes
            for process in processes:
                process.start()

            # Wait for the processes to finish
            for process in processes:
                process.join()

            # Fetch the results from each process
            result = []
            for parent_connection in parent_connections:
                l=parent_connection.recv()
                if(len(l) > 0):
                    #print(l)
                    self.addInteraction(l, datetime.now().date() + timedelta(days=day), bulk_write, populationStatuses)

        #result = popullation.bulk_write(bulk_write)

        return populationStatuses

if __name__ == '__main__':
    client = MongoClient(MONGO_CLUSTER)
    db = client.simulator
    popullation = db['popullation_{}'.format(50)]
    parallel = ParallelQuery()
    print("Initialization started")

    # Locations Dictionary
    allLocationsDict = dict()
    for activity in utils.locations:
        allLocationsDict[activity] = list(db.locations.find({"activity": activity}))[0]

    # Statuses Dictionary
    populationStatuses = dict()
    for person in list(popullation.find({}, {'_id': 0, 'person_id': 1, 'infection_status': 1})):
        populationStatuses[person['person_id']] = person['infection_status']

    statistics_per_day = []
    for day in range(0, 50):
        statuses = list(populationStatuses.values())
        statistics_per_day.append({'day': day, 'groups': dict(Counter(statuses))})
        populationStatuses = parallel.reviewLocations(popullation, day, allLocationsDict, populationStatuses)

