from collections import Counter
from interactionsGenerator import reviewLocations, fillMemcacheDict
import utils
from pymongo import MongoClient, WriteConcern, ReadPreference, InsertOne, UpdateOne
from pymongo.read_concern import ReadConcern
# import os
# import psutil
from secrets import MONGO_CLUSTER


def run_simulation(session, simulation_id, base_day, duration_in_days):
    """
    session: mongodb session
    simulation_id: integer
    base_day: integer, day in which the simulation begins
    duration_in_days: integer, simulation length

    Current behaviour:
        Simulates from base day to duration_in_days, assigning a new 
        random infection_status to each person. Each day a new 
        statistics object is created. the _id is the day of the 
        simulation, the value is a dictionary with a counter of each 
        infection_status. The last step is to update the
        infection_status in the population collection.

    Returns: Nothing (for now)
    """
    db = session.client.simulator
    #simulation = db['simulation_{}'.format(simulation_id)]
    population = db['popullation_{}'.format(simulation_id)]
    agenda = db.agenda
    infection_statistics = db.statistics

    # pprint(population)

    # Locations Dictionary
    allLocationsDict = dict()
    for activity in utils.locations:
        allLocationsDict[activity] = list(db.locations.find({"activity": activity}))[0]

    populationInfo = fillMemcacheDict(population, allLocationsDict)
    # process = psutil.Process(os.getpid())
    # # print(process.memory_info().rss)

    # Statuses Dictionary
    populationStatuses = dict()
    for person in list(population.find({}, {'_id': 0, 'person_id': 1, 'infection_status': 1})):
        populationStatuses[person['person_id']] = person['infection_status']

    statistics_per_day = []
    for day in range(base_day, duration_in_days):
        statuses = list(populationStatuses.values())
        statistics_per_day.append({'day': day, 'groups': dict(Counter(statuses))})
        # print(statistics_per_day)
        populationStatuses = reviewLocations(population, day, allLocationsDict, populationStatuses, populationInfo)
        # print(statistics_per_day)
        # for person_status in populationStatuses :
        #     person_status['infection_status'] = random.choice(['cured', 'susceptible', 'infectious', 'treated', 'infected'])
        # Concern: scaling. When dealing with huge datasets, can it be the case that it doesnt fit in memory?
    infection_statistics.insert_one({'_id': simulation_id, 'simulation': statistics_per_day})
        
    # bulk_write = []
    # for person_status in current_status:
    #     bulk_write.append(UpdateOne({'_id': person_status['_id']}, {'$set': {'infection_status': person_status['infection_status']}}))
    #
    # result = population.bulk_write(bulk_write, session=session)
    # return result

def callback(session, simulation_id, base_day, duration_in_days):
    run_simulation(session, simulation_id, base_day, duration_in_days)

def lambda_handler (event, context):
    operation = event['httpMethod']
    
    # Get the parameters from the UI by parsing the json file (body)
    parameters = json.loads(event['body'])
    sim_id = int(parameters['sim_id'])
    duration_in_days = int(parameters['days'])
    
    if operation == 'POST':
        client = MongoClient(MONGO_CLUSTER)
        wc_majority = WriteConcern("majority", wtimeout=1000)


        # Open a transaction to perform the following actions
        with client.start_session() as session:
            session.with_transaction(
                lambda s: callback(s, sim_id, 1, duration_in_days),
                read_concern=ReadConcern('local'),
                write_concern=wc_majority,
                read_preference=ReadPreference.PRIMARY)
        return {
            'statusCode': '400' if None else '200',
            'body': "Successfully run the simulation "+str(sim_id)
        }

def main():
    client = MongoClient(MONGO_CLUSTER)
    print("Initialization started")

    run_simulation(client.start_session(), 31, 0, 90)

    # for i in range(numDays):
    #     interactionsGen()

if __name__ == "__main__":
    main()