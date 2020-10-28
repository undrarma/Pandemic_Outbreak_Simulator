from pymongo import MongoClient
from secrets import MONGO_CLUSTER


def queryMongo(client):
    db = client.simulator
    activityDocs = db.agenda.find({"activity_id": "home"})
    for doc in activityDocs:
        print(doc)


# def respond(err):
#     return {
#         'statusCode': '400' if err else '200',
#         'body': "This is the response from Lambda POST."
#         }

def lambda_handler(event, context):
    operation = event['httpMethod']
    if operation == 'GET':
        # client = MongoClient(MONGO_CLUSTER)
        # print("connected")
        # queryMongo(client)
        return {
            'statusCode': '400' if None else '200',
            'body': "This is the response from Lambda GET."
        }
    elif operation == 'POST':
        return {
            'statusCode': '400' if None else '200',
            'body': "This is the response from Lambda POST."
        }

# def lambda_handler(event, context):
#     client = MongoClient(MONGO_CLUSTER)
#     print("connected")
#     queryMongo(client)
