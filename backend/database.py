import motor.motor_asyncio
import os, random, json
from model import DemoQuestion, User, Car
from utils import get_time, get_uuid, get_meta

# Read environment variables from meta file
meta = get_meta()
environment_vars = meta['env'][0]
cars_list = meta['cars']
questions = []

DB_NAME                     = environment_vars['database_name']
MAX_QUESTIONS_TO_GENERATE   = environment_vars['questions_to_generate']
CAR_SIMULATION              = environment_vars['car_simulation']
CAR_URL_TEMPLATE            = environment_vars['car_url_template']

# env variable overrides configuration in meta.json
DB_CONNECT_URL = os.environ.get('DB_CONNECT_URL',environment_vars['database_url'] )
VIRTUAL_EVENT  = os.environ.get('VIRTUAL_EVENT',environment_vars['virtual_event'] ) # Sandbox setup
print('VIRTUAL_EVENT=',VIRTUAL_EVENT)
try:
    print('Connecting to MongoDB with...',DB_CONNECT_URL)
    client = motor.motor_asyncio.AsyncIOMotorClient(DB_CONNECT_URL)
    client.server_info() # will throw an exception
except:
    print(f'Cannot connect to database with {DB_CONNECT_URL}')
    exit()
    
database = client[DB_NAME]

async def fetch_questions():
    global questions
    
    # Fetch all questions from DB
    collection = database.question
    cursor = collection.find({})
    async for document in cursor:
        questions.append(DemoQuestion(**document))
        
def get_environment_vars():
    return environment_vars

async def fetch_one_question(qnumber: str):
    collection = database.question
    document = await collection.find_one({"_id": qnumber})
    return document

async def fetch_many_questions(maxQuestions=MAX_QUESTIONS_TO_GENERATE):
    # Only return maxQuestions from the database in random order
    global questions

    # Generate a random list of maxQuestions questions from all questions in DB
    totalQuestions = len(questions)
    if (totalQuestions == 0 ):
        await fetch_questions()   # Just fetch it once from DB
        totalQuestions = len(questions)
        
    if (maxQuestions > 0):
        randomlist = random.sample(range(0, totalQuestions), maxQuestions )
    else:
        randomlist = random.sample(range(0, totalQuestions), totalQuestions)
    new_questions = list(map(questions.__getitem__, randomlist))

    return new_questions

# Create and register new user in DB, record startTime and return car id assigned to this user
async def create_user(user):
    collection = database.user
    print('Creating DB user ',user)
    user_in_db = await collection.find_one({"email": user.email.lower()})
    if( user_in_db ):
        print(f'User with email={user.email} already exists in database')
        if( 'timetaken' not in user_in_db ):  # User ind DB but had not finished or taken challenge
            print('User already registered but have not taken or completed challenge, permission to take challenge granted',user_in_db['_id'])
        else:
            print('User already registered and had taken the challenge')
            return {}
        return { "id": user_in_db['_id'] }
    user_id = get_uuid()
    document = { "_id": user_id, "email": user.email.lower(), "first": user.first, "last": user.last }
    result = await collection.insert_one(document)
    return { "id" :user_id }

async def fetch_user_by_id(userid: str):
    collection = database.user
    document = await collection.find_one({"_id": userid})
    return document

async def fetch_all_cars():
    global cars_list
    cars = []
    collection = database.car
    async for document in collection.find({}):
        cars.append(Car(**document))
    if len(cars) > 0:   # Load car info from DB to cars_list
        cars_list = list(map(lambda x: x.__dict__,cars))
    return cars
    
async def start_the_challenge(userid: str):
    epoch = round(get_time(False),2)                # record start time in car collection
    collection = database.car
    filter = { 'start': None }
    car = await collection.find_one(filter) # Find first available
    if( car ):
        print(f'car #{car["number"]} is assigned to user:{userid}')
        await collection.update_one(filter, {"$set": {"userid": userid,"start": epoch,"position": 0}})
        car = await collection.find_one({'number' : car['number']})
    return car

async def start_virtual_challenge(userid: str):
    epoch = round(get_time(False),2)                 # record start time in car collection
    collection = database.user
    filter = { '_id': userid }
    user = await collection.find_one(filter)
    if( user and ('timetaken' not in user) ):
        print(f'update user start time: {userid}, start: {epoch}')
        await collection.update_one(filter, {"$set": {"start": epoch}})
        user = await collection.find_one({'_id' : userid})
    elif user:
        print(f'user {userid} already taken the challenge') 
    return user

async def update_user_time(userid: str, carid: int):
    collection = database.car
    filter = {'number': carid}
    car = await collection.find_one(filter)
    print('update user time->',car)
    if car and 'start' in car:
        timetaken = get_time(False) - car['start']
        timetaken = round(timetaken,2)
        current_position = car['position']
        print(f'Time taken for user {userid} is {timetaken} secs')
    else:
        return 0
    collection = database.user
    filter = {'_id': userid }
    user = collection.find(filter)
    if( user and timetaken > 0):
        print(f'update user time: {userid}, timetaken: {timetaken}')
        await collection.update_one(filter, {"$set": {"timetaken": timetaken}})
        return current_position
    return 0

async def update_virtual_user_time(userid: str):
    epoch = get_time(False)
    collection = database.user
    filter = { '_id': userid }
    user = await collection.find_one(filter)
    if( user and 'start' in user ):
        start = user['start']
        if( start > 0 ):
            print(f'update virtual user time: {userid}, start: {start}, end: {epoch}')
            user['timetaken'] = round(epoch - start,2)
            # remove _id and optional fields before replace
            for key in { '_id','start' }:  
                if key in user:
                    user.pop(key)
            await collection.replace_one(filter,user)   
            user = await collection.find_one({'_id' : userid})
    return user

async def reset_car_in_db(carid: int) -> int:
    collection = database.car
    filter = {'number': carid}
    current_position = 0
    # Admin request to reset car record in DB and send it to starting position
    document = await collection.find_one(filter)
    if( document ):      
        current_position = document['position']
        document['position'] = 0                    
        # remove _id and optional fields before replace
        for key in { '_id','userid', 'start' }:  
            if key in document:
                document.pop(key)
        await collection.replace_one(filter,document)                             
    return current_position

async def fetch_leaderboard_users():
    collection = database.user
    users= []
    cursor = collection.find({})
    async for document in cursor:
        users.append(User(**document))
    return users

async def get_car_position( carid: int ) -> int:
    collection = database['car']
    filter = {'number': carid}
    document = await collection.find_one(filter)
    if( document ):
        return document['position']
    return 0

async def set_car_position( carid: int, position: int ):
    collection = database.car
    filter = {'number': carid}
    document = await collection.find_one(filter)
    if( document ):
        await collection.update_one(filter, {"$set": {"position": position}})
        return 1
    return 0
    
def get_car_payload(carid: int,weight: int):
    ''' Get car payload by car id (car number) and weight
    '''
    global cars_list
    car = cars_list[carid-1]   # current car
    print('Getting car payload, car#',carid,' weight=',weight)
    if weight != 0:
        car_url = CAR_URL_TEMPLATE % car['ip']
        if( weight <  -1):  # backup to starting position
            (speed,direction) = (car['backup_speed'],'backward')
        else:
            (speed,direction) = (car['speed'],'forward') if (weight > 0) else (car['speed'],'backward')
        payload = '{"speed": %s,"weight": %s, "direction": "%s"}' % (speed, abs(weight), direction)
        return (car_url,payload)
    else:
        return( None, None)
        