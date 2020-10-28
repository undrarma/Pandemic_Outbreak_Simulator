from pymongo import MongoClient
from db.secrets import MONGO_CLUSTER

def queryMongo(client):
    db = client.simulator
    activityDocs = db.agenda.find({"activity_id":"home"})
    for doc in activityDocs:
        print(doc)

def main():
    client = MongoClient(MONGO_CLUSTER)
    print("connected")
    queryMongo(client)

if __name__ == "__main__":
    main()