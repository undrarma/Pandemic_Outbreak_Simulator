# Tutorial Answers

## Question 1: Try to run again the same program by changing the connection string to use another user. Specifically, give as username the readOnly user and as password the password that you gave to this user. What is the error that you get? Why does this happen?
By running the same program as before, we are getting the following error:
```
Traceback (most recent call last):
  File "C:/Users/Alex/PycharmProjects/simulator/tutorial.py", line 23, in <module>
    population.insert_many(documents)
  File "C:\Users\Alex\Anaconda3\envs\neo4j_env\lib\site-packages\pymongo\collection.py", line 758, in insert_many
    blk.execute(write_concern, session=session)
  File "C:\Users\Alex\Anaconda3\envs\neo4j_env\lib\site-packages\pymongo\bulk.py", line 511, in execute
    return self.execute_command(generator, write_concern, session)
  File "C:\Users\Alex\Anaconda3\envs\neo4j_env\lib\site-packages\pymongo\bulk.py", line 346, in execute_command
    self.is_retryable, retryable_bulk, s, self)
  File "C:\Users\Alex\Anaconda3\envs\neo4j_env\lib\site-packages\pymongo\mongo_client.py", line 1384, in _retry_with_session
    return func(session, sock_info, retryable)
  File "C:\Users\Alex\Anaconda3\envs\neo4j_env\lib\site-packages\pymongo\bulk.py", line 341, in retryable_bulk
    retryable, full_result)
  File "C:\Users\Alex\Anaconda3\envs\neo4j_env\lib\site-packages\pymongo\bulk.py", line 295, in _execute_command
    result, to_send = bwc.execute(ops, client)
  File "C:\Users\Alex\Anaconda3\envs\neo4j_env\lib\site-packages\pymongo\message.py", line 899, in execute
    result = self.write_command(request_id, msg, to_send)
  File "C:\Users\Alex\Anaconda3\envs\neo4j_env\lib\site-packages\pymongo\message.py", line 988, in write_command
    reply = self.sock_info.write_command(request_id, msg)
  File "C:\Users\Alex\Anaconda3\envs\neo4j_env\lib\site-packages\pymongo\pool.py", line 690, in write_command
    helpers._check_command_response(result)
  File "C:\Users\Alex\Anaconda3\envs\neo4j_env\lib\site-packages\pymongo\helpers.py", line 159, in _check_command_response
    raise OperationFailure(msg % errmsg, code, response)
pymongo.errors.OperationFailure: user is not allowed to do action [insert] on [tutorial.population]
```
The reason is that we are trying to write a couple of collections to our database by using the **readOnly** user whose rights are limited to **reading**.

## Question 2: Create a python script that this user will be able to run. Get the person_id of the documents that have infection_status: "infected".
Below is the python code that fetches the `tutorial.population` collection and filters only those persons that have `"infection_status": "infected"`.
```py
import os
from pymongo import MongoClient

MONGO_CLUSTER = os.getenv('MONGO_CLUSTER')
client = MongoClient(MONGO_CLUSTER)
db = client.tutorial
population = db.population

query = {"infection_status": "infected"}
result = population.find(query, { "person_id": 1, "_id": 0})
for document in result:
    print(document)
```
## Question 3: What is going to happen when you use the tutorialUser that has the custom role. If this user has not the required privileges to run the program of Question 2, try to modify its rights according to the principle of minimal privilege.
In this case, we are getting the same error that we get in Question 1 but not for the same reason. Here, we are trying to read from a collection 
with a user that has read and write permissions but not for the collection that we are trying to read from.
</br>
To tackle this problem we need to edit the **role** of this user by changing the allowed actions that he can do 
to **find** only (it can be found inside **Collection Actions/Query and Write Actions** menu) and by also changing 
the collection that this role is applied from **car** to **population**. These changes should be performed in the 
Database Access tab.
</br>
In this way, we assign to this user the least required privileges.
</br>
</br>
It would be wrong to change this role from the **Database Access** panel, as in this case we would 
modify the role by giving him access to **ALL** the databases hosted in our cluster, which obviously does not 
correspond to the principle of minimal privilege!

## Question 4: Create a trigger for the previously created cluster that will check the correctness of the data in your population. Specifically, every time that an invalid infection status is inserted in your population collection, write the person_id and the wrong value that was inserted. The valid values for the infection status are: 'susceptible',  'infected', 'infectious', 'treated' and 'cured'.
The required JavaScript is the following:
```js
exports = function(changeEvent) {

    var valid_values = ['susceptible',  'infected', 'infectious', 'treated', 'cured'];

    // Get the full Document
    const fullDocument = changeEvent.fullDocument;

    // If the newly inserted value for the infection status is not valid
    // log an error
    if(!valid_values.includes(fullDocument.infection_status))
    {
      console.log("person_id: "+fullDocument.person_id);
      console.log("infection_status: "+fullDocument.infection_status);
    }
};

```

## Question 5: After having your trigger enabled, try to insert a document with an invalid infection status and check the logs. In addition, instead of inserting, try to update the infection status to a wrong value and check the logs again.
In both cases, you should see a log record with similar content to the following:
</br>
```
Logs:
[
  "person_id: 1",
  "infection_status: infectedddddd"
]
```
The above log depicts that we inserted an invalid infection status for the person with id = 1 and that the wrong value was infectedddddd.
</br>
![Log record](img/log_example.PNG)
We can also see some additional information about when the trigger was called, how much time took to terminate etc...


### Question 6:

Number of people per country:

db.adult.aggregate({$group: { _id: "$native_country", count: {$sum:1}}})

Total number of people:

db.adult.count()

There are 5001 lines in the csv and tsv files. The first one is the header, so there are 5000 people in each file.
The total number of people is 30000. If 10000 out of them are in the csv and tsv file, there will be 20000 people between the avro and parquet files (we cannot count them with wc due to the difference in format).

### Question 7:

db.adult.aggregate({$group: { _id: "$native_country", average: {$avg:"$capital_gain"}}})