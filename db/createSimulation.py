import numpy as np
import random
import json
from collections import Counter
import numexpr as ne
import time
import multiprocessing as mp

from pymongo import MongoClient, WriteConcern, ReadPreference
from pymongo.read_concern import ReadConcern

from secrets import MONGO_CLUSTER

def statistics_translator(original_dict):
    translated_dict = dict()
    translated_keys = ['susceptible', 'incubating', 'infected', 'treated', 'cured', 'dead']
    for key in original_dict.keys():
        translated_dict[translated_keys[key]] = original_dict[key]
    return translated_dict

def get_random_locations(home, recreational_places, n):
    """
        Samples (with replacement) n elements from a list.
        This is supposed to be the simulation of the agenda
        of a person after work. The person can go either to
        his/her home or to recreational places.
    """
    return list(np.random.choice(recreational_places + home, n))


def generate_statuses(n, statuses_weights):
    """
        Generates an np array of int8 with n elements.
        Receives n and a list of floats (weights of statuses).
            Assumption: The 6 floats sum up to 1
        There are 6 statuses:
            - 0: Susceptible (healthy / not in contact with disease)
            - 1: Incubating (not infected yet, but will soon)
            - 2: Infected (infected and infectious)
            - 3: Treated (infected and infectious, but less likely to die)
            - 4: Cured (healthy / immune)
            - 5: Dead
    """
    statuses = np.array(random.choices(range(6), weights=statuses_weights, k=n), dtype='int8')

    return statuses

def simulationExists(client, user_id, simulation_name):
    db = client.simulator
    user_map_simulation = db.user_simulation
    simulation_exists = {"user_id": user_id,
                             "simulations": {"$elemMatch": {"simulation_name": simulation_name} }
                           }
    user_collection = user_map_simulation.find_one(simulation_exists)

    if user_collection is None:
        return 0
    else:
        return 1

def generate_locations(n):
    """
        Generates a 24 * n 2d np array of int16/int32 (depending on n).
        With 16 bits we can have 2^15 different int values (this is the
        reason for the checking in the first line of the function)
        Receives n.
        For the sake of simplicity, all people will be 8 hours at home,
        8 hours at work and 8 hours at random places between
        recreational and home.
    """
    dtype = 'int16' if 2 ** 15 > n else 'int32'
    places_home = np.array(random.choices(range(int(.8 * n)), k=n), dtype)
    places_work = np.array(random.choices(range(int(.8 * n), int(.9 * n)), k=n), dtype)
    places_recreational = np.array([random.choices(range(n), k=8) for i in range(n)], dtype)
    agendas = np.array([[places_home[i]] * 8 + [places_work[i]] * 8 + list(places_recreational[i]) for i in range(n)],
                       dtype)

    return agendas


# @profile
def generate_population_info(population_arguments):
    '''
        This function generates the population infos calling several functions and
        returns a dictionary that contains them
        Assumption: population IDs are just numbers from 0 to N
    '''

    # Generate statuses
    statuses = generate_statuses(population_arguments['population_size'], population_arguments['statuses_weights'])
    # Generate locations (24 locations per person)
    locations = generate_locations(population_arguments['population_size'])
    # Generate days in current status (initialized at 0)
    days_in_current_status = np.zeros(population_arguments['population_size'], dtype='int8')

    dict_population_info = dict()

    dict_population_info['statuses'] = statuses
    dict_population_info['locations'] = locations
    dict_population_info['days_in_current_status'] = days_in_current_status

    return dict_population_info


# @profile
def simulate_day(dict_population_info):
    """
        Simulates a day in a simulation. Returns a set with the people
        likely to have been infected. takes the locations visited by
        more than one person each hour and, if one of the visitors
        has the virus, inserts that visitor in a set.
        Returns the set as a list.
    """
    locations = dict_population_info['locations']
    statuses = dict_population_info['statuses']
    possibly_infected = []

    times = [0, 0]

    for hour in np.transpose(locations):
        # Get all the groups in places with more than 1 person in this hour
        all_groups = [[x for x in np.arange(len(statuses)) if hour[x] == place] for place in
                      [k for k, v in Counter(hour).items() if v > 1]]
        # All the people that have had interaction with infected people
        possibly_infected += [item for item in all_groups if any([statuses[i] == 2 for i in item])]

    answer = np.unique([item for sublist in possibly_infected for item in sublist])
    return [x for x in answer if statuses[x] == 0]


# This function will be the work of every
# slave process
def executeQuery(places, statuses, hour, conn):
    # list of infected people
    possibly_infected = []

    all_groups = [[x for x in np.arange(len(statuses)) if hour[x] == place] for place in places]
    possibly_infected += [item for item in all_groups if any([statuses[i] == 2 for i in item])]

    conn.send(possibly_infected)
    conn.close()

# @profile
# @profile
def simulate_day_parallel(dict_population_info):
    """
        Simulates a day in a simulation. Returns a set with the people
        likely to have been infected. takes the locations visited by
        more than one person each hour and, if one of the visitors
        has the virus, inserts that visitor in a set.
        Returns the set as a list.
    """
    locations = dict_population_info['locations']
    statuses = dict_population_info['statuses']
    possibly_infected = []

    times = [0, 0]

    # start the workers
    NUM_OF_PROCESSES = mp.cpu_count()

    count=0

    # for every hour
    possibly_infected = []
        
    for hour in np.transpose(locations):
        #beft = time.time()
        processes = []
        parent_connections = []
        tempC = []
        for place in [k for k, v in Counter(hour).items() if v > 1]:
            tempC.append(place)

        # Split places
        start = 0

        for p in range(0,NUM_OF_PROCESSES):
            # Add to the parent_connection the new pipe
            parent_conn, child_conn = mp.Pipe()
            parent_connections.append(parent_conn)
            end = start + int(len(tempC)/NUM_OF_PROCESSES)

            # if it's not the last process
            if p != NUM_OF_PROCESSES-1:
                process = mp.Process(target=executeQuery, args=(tempC[start:end], statuses, hour, child_conn,))
            else:
                process = mp.Process(target=executeQuery, args=(tempC[start:], statuses, hour, child_conn,))
            processes.append(process)
            start += int(len(tempC)/NUM_OF_PROCESSES)

        # Launch all the processes
        for process in processes:
            process.start()

        # Wait for the processes to finish
        for process in processes:
            process.join()

        # Receive the message from all the child processes (list of susceptible people)
        for parent_connection in parent_connections:
            possibly_infected+=parent_connection.recv()

        #aftt = time.time()

    answer_par = np.unique([item for sublist in possibly_infected for item in sublist])
    return [x for x in answer_par if statuses[x] == 0]


def infect_people(susceptible_set, days, statuses, infection_rate):
    '''
        From the susceptible people samples a percentage and change the
        status of each sampled person to incubating
    '''
    number_people_to_infect = int((len(susceptible_set)) * infection_rate)
    new_infected = random.sample(susceptible_set, number_people_to_infect)
    for i in range(number_people_to_infect):
        statuses[new_infected[i]] = 1
        days[new_infected[i]] = 1
    return statuses, days


def update_statuses_and_days(statuses, days, MORTALITY_RATE):
    '''
        For each person it performs dfferent operation based on the status
        In case of:
        - 0,4,5 (susceptible,immune or dead) do nothing
        - 1 (incubating) either keep the current status or move to infected
        - 2 (infected) either keep the current status or change to dead, treated or immune
        - 3 (treated) either keep the current status or change to dead or immune
    '''
    TREATED_RATE = 0.5
    perc_mortality_and_infected = MORTALITY_RATE + TREATED_RATE
    for i in range(len(statuses)):
        if (statuses[i] in [0, 4, 5]):  # susceptible
            continue
        elif (statuses[i] == 1):  # incubating
            if (days[i] == 3):
                statuses[i] = 2
                days[i] = 0
        elif (statuses[i] == 2):  # infected
            '''
                For the first 5 days it stays infected. 
                From the sixth day, samples a number K from 0 to 99.
                If K is less than the cumulate probability until cumulative = MORTALITY_RATE*100, the person dies 
                if K is less than the cumulate probability until cumulative = (cumulative + TREATED_RATE) * 100, the people get treated
                If K is less than the cumulate probability until cumulative = cumulative + (100 - cumulative )/3, the person remains infected
                If K is greather than the cumulate probability cumulative, the person becomes immune
            '''
            if (days[i] < 5):
                continue
            else:
                sampled = random.randint(0, 99)
                if (sampled <= MORTALITY_RATE * 100):  # dead
                    statuses[i] = 5
                elif (sampled <= perc_mortality_and_infected * 100):  # treated
                    statuses[i] = 3
                    days[i] = 0
                elif (sampled <= ((
                                          99 - perc_mortality_and_infected * 100) / 3 + perc_mortality_and_infected * 100)):  # still infected
                    continue
                else:  # immune
                    statuses[i] = 4
        elif (statuses[i] == 3):  # treated
            '''
                For the first 4 days it stays treated. 
                From the fifth day, samples a number K from 0 to 99.
                If K is less than the cumulate probability until cumulative = MORTALITY_RATE/2*100, the person dies 
                if K is less than the cumulate probability until cumulative = (cumulative + TREATED_RATE*0.3) * 100, the people remains treated
                If K is greather than the cumulate probability cumulative, the person becomes immune
            '''
            if (days[i] < 4):
                continue
            else:
                sampled = random.randint(0, 99)
                if (sampled <= MORTALITY_RATE * 50):  # dead
                    statuses[i] = 5
                elif (sampled <= perc_mortality_and_infected * 30):  # still treated
                    continue
                else:  # immune
                    statuses[i] = 4

    return statuses, days


def run_simulation(parameters):
    dict_population_info = generate_population_info(parameters)
    days = dict_population_info['days_in_current_status']
    statuses = dict_population_info['statuses']
    locations = dict_population_info['locations']

    statistics = []

    for day in range(parameters['days']):
        counters = Counter(statuses)
        statistics.append({'day': day, 'groups': statistics_translator(dict(counters))})
        if (counters[1] == 0) & (counters[2] == 0) & (counters[3] == 0):
            break

        possibly_infected = simulate_day_parallel(dict_population_info)

        # The day passes
        days = ne.evaluate("days + 1")

        statuses, days = infect_people(list(possibly_infected), days, statuses, parameters['infection_rate'])

        statuses, days = update_statuses_and_days(statuses, days, parameters['mortality_rate'])

    # Statistics
    document = {'simulation': statistics, 'mortality_rate': parameters['mortality_rate'],
                'infection_rate': parameters['infection_rate']}

    return document

def writeStatistics(session, simulation_id, document):
    db = session.client.simulator
    infection_statistics = db.statistics
    document['_id'] = simulation_id
    infection_statistics.insert_one(document, session=session)
    return

def createSimulation(session, user_id, simulation_name):
    db = session.client.simulator
    globalVariables = db.global_variables

    # Get the current max simulation id
    max_sim_id = globalVariables.find_one({"attribute_name": "simulation_counter"}, {"value": 1, "_id": 0})
    max_sim_id = max_sim_id['value'] + 1

    # Update max simulation id
    update_max_simid = {"attribute_name": "simulation_counter"}
    newvalues = {"$set": {"value": max_sim_id}}
    globalVariables.update_one(update_max_simid, newvalues, session=session)

    # Map the new simulation with its user
    user_map_simulation = db.user_simulation
    find_user_collection = {"user_id": user_id}
    user_collection = user_map_simulation.find_one(find_user_collection)

    # This user does not have any simulation
    if (user_collection is None):
        map_document = {
            "user_id": user_id,
            "simulations": [{"simulation_id": max_sim_id, "simulation_name": simulation_name}]
        }
        success = user_map_simulation.insert_one(map_document, session=session)

    # If the user has also other simulations, add the new simulation to his lest
    else:
        newvalues = {"$push": {"simulations": {"simulation_id": max_sim_id, "simulation_name": simulation_name}}}
        success = user_map_simulation.update_one(find_user_collection, newvalues, session=session)

    return max_sim_id


def callback(session, user_id, simulation_name, sim_statistics):
    # Save the information to the database
    sim_id = createSimulation(session, user_id, simulation_name)
    writeStatistics(session, sim_id, sim_statistics)

    return sim_id


def lambda_handler(event, context):
    operation = event['httpMethod']

    # Get the parameters from the UI by parsing the json file (body)
    parameters = json.loads(event['body'])

    if operation == 'POST':
        client = MongoClient(MONGO_CLUSTER)

        # Check the validity of the simulation name
        user_id = parameters['username']
        simulation_name = parameters['simname']
        if (simulationExists(client, user_id, simulation_name)):
            return {
                'statusCode': '401',
                'body': "Simulation name already exists for this user. Please provide a different simulation name."
            }

        wc_majority = WriteConcern("majority", wtimeout=1000)

        # Run a new simulation
        parameters2 = dict()
        parameters2['population_size'] = int(parameters['population'])
        parameters2['statuses_weights'] = [float(parameters['susceptibility'])/100,
                                          float(parameters['infectious'])/100, float(parameters['contagious'])/100,
                                          float(parameters['treatment'])/100, float(parameters['cure'])/100, .0]
        parameters2['mortality_rate'] = float(parameters['mortality_rate'])/100
        parameters2['infection_rate'] = float(parameters['infection_rate'])/100
        parameters2['days'] = int(parameters['days'])
        sim_statistics = run_simulation(parameters2)

        # Open a transaction to perform the following actions
        # Create a new simulation
        with client.start_session() as session:
            sim_id = session.with_transaction(
                lambda s: callback(s, user_id, simulation_name, sim_statistics),
                read_concern=ReadConcern('local'),
                write_concern=wc_majority,
                read_preference=ReadPreference.PRIMARY)
        return {
            'statusCode': '400' if None else '200',
            'body': "Successfully created the new simulation " + str(sim_id)
        }
