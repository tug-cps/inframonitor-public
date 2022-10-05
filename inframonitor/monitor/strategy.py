from common.log import log, dbg
from .helpers import (filter_none_values, time_from_string)


def value_exceeds_prediction(data, sensor, sensor_name, db, tsdb) -> bool:
    """
    (1) reading is 1.3 times higher than the highest value ever predicted (up to now)
    """
    latest_entry = data[-1]
    reading = latest_entry['reading']
    prediction = latest_entry['prediction']

    def recalculate_max():
        max_prediction = sensor.get('maxPrediction')
        if not max_prediction:
            log('No max prediction value in mongodb, querying predicted values of the last 3 months...')
            all_values = tsdb.get(sensor_name, '90d')
            max_prediction = max(filter_none_values([p.get('prediction') for p in all_values]))
            db.update(sensor['_id'], {'maxPrediction': max_prediction})
        elif prediction > max_prediction:
            log('Prediction for now is > max prediction, saving max prediction to mongodb')
            max_prediction = prediction
            db.update(sensor['_id'], {'maxPrediction': max_prediction})
        return max_prediction

    # compare new prediction with max prediction
    max_prediction = recalculate_max()
    dbg("max prediction:", max_prediction, "prediction:", prediction, "reading:", reading)
    if reading > max_prediction * 1.3:
        log(f'Anomaly detected: Current value ({reading}) > max ({max_prediction}) * 1.3')
        return True
    return False


def value_continuously_exceeds_prediction(data) -> bool:
    """
    (2) reading is 1.3 times higher than the prediction 3 times in a row
    """

    def readings_greater_predictions(entries, factor):
        for entry in entries:
            if entry['reading'] <= entry['prediction'] * factor:
                return False
        return True

    if readings_greater_predictions(data[-3:], 1.3):
        log('Anomaly detected: Readings are greater than predictions * 1.3 for at least 3 times in a row')
        # [log(d) for d in data[-3:]]
        return True
    return False


def value_is_not_zero_over_night(data, sensor, sensor_name, db, tsdb) -> bool:
    """
    (3) readings never reach lowest value ever predicted between 22:00 and 04:00
    """

    def filter_timestamps(entry):
        timestamp = time_from_string(entry['time'])
        # FIXME check time zone difference
        return timestamp.hour >= 21 or timestamp.hour <= 3

    def calculate_min_prediction(entries):
        def filter_empty_predictions(entry):
            p = entry.get('prediction')
            return p and p >= 0

        return min([e['prediction'] for e in filter(filter_empty_predictions, entries)])

    def recalculate_min(current_min, sensor, sensor_name):
        min_prediction = sensor.get('minPrediction')
        if not min_prediction:
            log('No min prediction value in mongodb, querying predicted values of the last 3 months...')
            all_entries = tsdb.get(sensor_name, '90d')
            filtered_entries = filter(filter_timestamps, all_entries)
            min_prediction = calculate_min_prediction(filtered_entries)
            db.update(sensor['_id'], {'minPrediction': min_prediction})
        elif current_min < min_prediction:
            log('Prediction for now is < min prediction, saving min prediction to mongodb')
            min_prediction = current_min
            db.update(sensor['_id'], {'minPrediction': min_prediction})
        return min_prediction

    filtered_data = list(filter(filter_timestamps, data))
    current_min = calculate_min_prediction(filtered_data)
    min_prediction = recalculate_min(current_min, sensor, sensor_name)
    dbg("min prediction:", min_prediction, "current min:", current_min)

    def readings_reach_min_prediction(entries, min_prediction):
        for entry in entries:
            if entry['reading'] <= min_prediction:
                return True
        return False

    if not readings_reach_min_prediction(filtered_data, min_prediction):
        log('Anomaly detected: Readings between 22:00 and 04:00 never reach min prediction')
        # [log(d) for d in filtered_data]
        return True
    return False


def value_does_not_change(data) -> bool:
    def all_readings_are_identical(entries):
        readings = [entry['reading'] for entry in entries]
        return readings.count(readings[0]) == len(readings)

    if all_readings_are_identical(data):
        log('Anomaly detected: No change in readings for >= 24h')
        return True
    return False
