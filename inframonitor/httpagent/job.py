import datetime as dt
import os

import requests
from pymongo import MongoClient

from common import database
from common.log import log

API_KEY = os.environ.get('METEOBLUE_API_KEY', 'deadbeef')


def job():
    log('Polling job starting...')
    log('Connecting to database...')
    client: MongoClient = database.get_db().client
    db = client.get_database('ontology')
    coll = db.get_collection('meteoblue')

    log('Polling http api...')
    uri = 'https://my.meteoblue.com/packages/basic-1h_wind-1h_clouds-1h_solar-1h' \
          f'?apikey={API_KEY}' \
          f'&lat=47.0667' \
          f'&lon=15.45' \
          f'&asl=363' \
          f'&format=json' \
          f'&tz=Europe%2FVienna'

    r = requests.get(uri)
    r.raise_for_status()
    log('Success, writing to database...')

    document = {
        'timestamp': dt.datetime.utcnow(),
        'data': r.json()
    }
    result = coll.insert_one(document)
    assert result.acknowledged
    log('Done.')


if __name__ == '__main__':
    job()
