import datetime as dt
import traceback

from common import database
from common.log import log, err, warn
from common.type_def import building_types
from prediction import predictor


def job(invocation_time=None, forecast_hours=72):
    if invocation_time is None:
        invocation_time = dt.datetime.utcnow()

    invocation_time = invocation_time.replace(minute=0, second=0, microsecond=0)
    log(f'Updating predictions starting from {invocation_time.isoformat()} +{forecast_hours}h')

    tsdb = database.get_tsdb()
    db = database.get_db()
    sensors = db.find({'type': {'$nin': building_types}})
    log(f'Found {len(sensors)} sensors in mongodb')

    skipped_updates = []
    successful_updates = []
    error_updates = []

    # predict for correct timezone -> model is trained on Graz timezone, because
    # it changes for daylight savings. this prevents a 1h offset when time
    # changes to daylight savings and back.
    # timezone = pytz.timezone('Europe/Berlin')
    # start_time = invocation_time.replace(tzinfo=timezone)

    for sensor in sensors:
        sensor_name = sensor['name']
        try:
            # if predictor.static_model_exists(sensor_name):
            #     points = predictor.predict(sensor_name, start_time, forecast_hours)
            if predictor.pv_model_exists(sensor_name):
                points = predictor.predict_pv(sensor_name)
            else:
                skipped_updates.append(sensor)
                continue

            tsdb.upsert_many(points, tags={'sensor': sensor_name})
            successful_updates.append(sensor)

        except Exception as e:
            err(f'Cannot upsert prediction for sensor {sensor_name} to influxdb.')
            err(e)
            err(traceback.format_exc())
            error_updates.append(sensor)

    warn(f'Skipped {len(skipped_updates)} sensors with missing models')

    if error_updates:
        err(f'Errors occured during updating {len(error_updates)} sensors')
        [err(' ', update['_id']) for update in error_updates]

    log(f'Updated {len(successful_updates)} sensors:')
    [log(' ', update['_id']) for update in successful_updates]


if __name__ == '__main__':
    job()
