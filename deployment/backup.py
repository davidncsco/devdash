#!/usr/bin/python
import os, sys, datetime, tarfile, os.path
from pymongo import MongoClient
from bson.json_util import dumps


def create_folder_backup(dbname):
    dt = datetime.datetime.now()
    directory = ('backups/bk_%s_%s-%s-%s__%s_%s' % (dbname,dt.month,dt.day,dt.year, dt.hour, dt.minute))
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def run_backup(mongoUri, dbname, dbcollection):
    try:
        client = MongoClient(mongoUri)
        client.server_info() # will throw an exception
    except:
        print(f'Cannot connect with {mongoUri}')
        exit()
    db = client[dbname]
    collections = db.list_collection_names()
    files_to_compress = []
    directory = create_folder_backup(dbname)
    for collection in collections:
        if( dbcollection == collection ):
            db_collection = db[collection]
            cursor = db_collection.find({})
            filename = ('%s/%s.json' %(directory,collection))
            files_to_compress.append(filename)
            with open(filename, 'w') as file:
                file.write('[')
                for document in cursor:
                    file.write(dumps(document))
                    file.write(',')
                file.write(']')
    tar_file = ('%s.tar.gz' % (directory)) 
    #make_tarfile(tar_file,files_to_compress)

def make_tarfile(output_filename, source_dir):
    tar = tarfile.open(output_filename, "w:gz")
    for filename in source_dir:
        tar.add(filename)
    tar.close()

if __name__ == '__main__':
    # Backup the 'user' collection in DB. This script can be run as a crontab
    # e.g. Run backup every 5 minutes 
    # 5/* * * * * /usr/bin/python3 /home/devnet/backup
    # env variable overrides configuration in meta.json
    DB_CONNECT_URL = os.environ.get('DB_CONNECT_URL','mongodb://davidn:ciscopsdt@10.0.0.60:27017/' )
    DB_NAME        = "devrel500"
    try:
        run_backup(DB_CONNECT_URL, DB_NAME, "user")
        print('[*] Successfully performed backup')
    except Exception as e:
        print('[-] An unexpected error has occurred')
        print('[-] '+ str(e) )
        print('[-] EXIT')
