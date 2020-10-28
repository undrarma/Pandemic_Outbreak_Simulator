from pymongo import MongoClient, WriteConcern, ReadPreference
from pymongo.read_concern import ReadConcern

from secrets import MONGO_CLUSTER

import json

def simulationValid(client, username, simulation_name):
    db = client.simulator
    user_map_simulation = db.user_simulation
    simulation_exists = {"user_id": username,
                             "simulations": {"$elemMatch": {"simulation_name": simulation_name} }
                           }
    user_collection = user_map_simulation.find_one(simulation_exists, {"simulations": 1, "_id": 0})

    # Simulation not found
    if user_collection is None:
        return -1

    for elem in user_collection:
        for i in user_collection[elem]:
            # Simulation found
            if(i['simulation_name'] == simulation_name):
                return i['simulation_id']

    # Simulation not found
    return -1

def getStatistics(client, username, simulation_id):
    db = client.simulator
    statistics_docs = db.statistics

    answer = {}

    mortality_rate = statistics_docs.find({"_id" : simulation_id}).next()["mortality_rate"]
    infection_rate = statistics_docs.find({"_id" : simulation_id}).next()["infection_rate"]
    statistics_list = statistics_docs.find({"_id" : simulation_id}).next()["simulation"]
    
    answer['incubating'] = [item["groups"]["incubating"] if "incubating" in item["groups"] else 0 for item in statistics_list]
    answer['treated'] = [item["groups"]["treated"] if "treated" in item["groups"] else 0 for item in statistics_list]
    answer['susceptible'] = [item["groups"]["susceptible"] if "susceptible" in item["groups"] else 0 for item in statistics_list]
    answer['infected'] = [item["groups"]["infected"] if "infected" in item["groups"] else 0 for item in statistics_list]
    answer['cured'] = [item["groups"]["cured"] if "cured" in item["groups"] else 0 for item in statistics_list]
    answer['dead'] = [item["groups"]["dead"] if "dead" in item["groups"] else 0 for item in statistics_list]

    # Return first and last days statuses
    answer['incubating_day1'] = answer['incubating'][0]
    answer['treated_day1'] = answer['treated'][0]
    answer['susceptible_day1'] = answer['susceptible'][0]
    answer['infected_day1'] =answer['infected'][0]
    answer['cured_day1'] = answer['cured'][0]
    answer['dead_day1'] = answer['dead'][0]

    answer['incubating_daylast'] = answer['incubating'][-1]
    answer['treated_daylast'] = answer['treated'][-1]
    answer['susceptible_daylast'] = answer['susceptible'][-1]
    answer['infected_daylast'] =answer['infected'][-1]
    answer['cured_daylast'] = answer['cured'][-1]
    answer['dead_daylast'] = answer['dead'][-1]
    
    # Return the simulation's parameters
    answer['population'] =  answer['incubating'][0]+answer['treated'][0]+answer['susceptible'][0]+answer['infected'][0]+answer['cured'][0]+answer['dead'][0]
    answer['mortality_rate'] = str(mortality_rate*100)+"%"
    answer['infection_rate'] = str(infection_rate*100)+"%"


    return answer

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': json.dumps(str(err) if err else res),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
    }
    

def lambda_handler(event, context):
    operation = event['httpMethod']
    parameters = json.loads(event['body'])

    if operation == 'POST':
        client = MongoClient(MONGO_CLUSTER)
        
        # Check that the given simulation name is valid for the current user
        sim_id = simulationValid(client, parameters['username'], parameters['simname'])
        if(sim_id == -1):
            return {
                'statusCode': '402',
                'body': 'You do not have any simulation with name ' + parameters['simname'] + '\n' + 'Please provide another name'
                }
        
        # If the simulation name is valid, return the statistics
        return respond(None, getStatistics(client, parameters['username'], sim_id))
    else:
        return respond(ValueError('Unsupported method %s'%operation))
