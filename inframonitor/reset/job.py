import traceback

from common import database
from common.log import err, log, warn


def try_reset_sensor(db, _id):
    try:
        if not db.update(_id, {'reading': 0}):
            warn(f'Mongodb returned False when updating sensor {_id}')
        return True
    except Exception:
        err('Error when updating sensor', _id, traceback.format_exc())


def job(db=None):
    log('Resetting people counter values...')

    if not db:
        db = database.get_db()

    sensors = db.find_simple('type', 'People')
    successful_updates = [sensor['_id'] for sensor in sensors if try_reset_sensor(db, sensor['_id'])]

    log(f'Updated {len(successful_updates)} sensors:')
    [log(' ', update) for update in successful_updates]


if __name__ == '__main__':
    job()
