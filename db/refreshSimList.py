from pymongo import MongoClient, WriteConcern, ReadPreference

from secrets import MONGO_CLUSTER

import json

def refreshList(client, username):
    db = client.simulator
    user_map_simulation = db.user_simulation
    simulation_exists = {"user_id": username}
    user_collection = user_map_simulation.find_one(simulation_exists, {"simulations": 1, "_id": 0})

    return json.dumps(user_collection['simulations'])

def lambda_handler(event, context):
    operation = event['httpMethod']
    parameters = json.loads(event['body'])

    if operation == 'POST':
        client = MongoClient(MONGO_CLUSTER)
        respond = refreshList(client, parameters['username'])

        return {
            'statusCode': '200',
            'body': respond
        }
    else:
        return {
            'statusCode': '400',
            'body': 'Unsupported method %s'%operation
        }
