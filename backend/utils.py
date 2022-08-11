"""UTILS
Misc helpers/utils functions
"""

# # Native # #
from pymongo import MongoClient
import os, json
from time import time
from uuid import uuid4
from typing import Union

__all__ = ("get_time", "get_uuid", "get_meta", "load_db")


def get_time(seconds_precision=True) -> Union[int, float]:
    """Returns the current time as Unix/Epoch timestamp, seconds precision by default"""
    return time() if not seconds_precision else int(time())


def get_uuid() -> str:
    """Returns an unique UUID (UUID4)"""
    return str(uuid4())

def get_meta() -> list:
    # Read configurable variables from META file
    META = './data/meta.json'
    data = {}
    with open(META) as f:
        data = json.load(f)

    return data

def load_db():
    ''' Initialize question and car collections in the DB (like running loaddb.py)
    '''
    meta = get_meta()
    if( len(meta) == 0 ):
        print('Cannot read META data')
        return
    
    env_vars = meta['env'][0]
    DB_CONNECT_URL = os.environ.get('DB_CONNECT_URL',env_vars['database_url'] )
    DB_NAME        = env_vars['database_name'] 
    try:
        print('Connecting to MongoDB...')
        client = MongoClient(DB_CONNECT_URL)
        client.server_info() # will throw an exception
    except:
        print(f'Cannot connect with {DB_CONNECT_URL}')
        exit()
 
    database = client[DB_NAME]
    collection = database.question
    print ('Loading questions database...',end="")
    for i in meta['questions']:
        filter = { '_id':i['_id'] }
        if( collection.find_one(filter) ):       # If exists then update/replace with new values
            print(i["_id"],end='..')
            key = i.pop('_id')
            collection.replace_one( {'_id':key}, i )
        else:
            print(f'inserting -> Question#{i["_id"]} with image {i["filename"]}')
            collection.insert_one(i)
    print('...Done')

    # Loading Race Cars Database
    collection = database.car
    print ('Loading race cars database...',end="")
    for i in meta['cars']:
        filter = {"number":i['number']}
        if( collection.find_one(filter) ):
            print(i["number"],end='..')
            collection.replace_one( filter, i )
        else:
            print(f'inserting race car#{i["number"]} with IP={i["ip"]}')
            collection.insert_one(i)
    print('...Done')
