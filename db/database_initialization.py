import random
import utils

from pymongo import MongoClient
from secrets import MONGO_CLUSTER

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
    
    statistics = db.statistics
    statistics.insert_one({"_id": -1})

def main():
    client = MongoClient(MONGO_CLUSTER)
    print("Initialization started")

    initializeGlobalVariables(client)

if __name__ == "__main__":
    main()
