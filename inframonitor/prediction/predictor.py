import datetime as dt
import importlib
from pathlib import Path

import numpy as np
import pandas as pd
from pvlib import solarposition

from common import database
from common.dbwrapper.influxdbwrapper import MeasurementPoint
from .datamodels import datamodels as dm


def get_model_path(sensor_name: str, model_dir) -> Path:
    return Path(__file__).parent.joinpath(model_dir).joinpath(sensor_name)


def static_model_exists(sensor_name: str):
    return get_model_path(sensor_name, 'models').exists()


def pv_model_exists(sensor_name: str):
    return get_model_path(sensor_name, 'models_pv').exists()


def load_model_for_sensor(model_path: Path) -> dm.Model:
    return dm.Model.load(str(model_path))


def generate_time_steps(start_time: dt.datetime, hours: int = 1):
    if hours < 1:
        raise ValueError('You must generate time steps for at least one hour')
    return np.array([start_time + dt.timedelta(hours=h) for h in range(hours)])


def predict(sensor_name: str, start_time: dt.datetime, hours: int):
    model_path = get_model_path(sensor_name, 'models')
    if not model_path.exists():
        raise FileNotFoundError

    model = load_model_for_sensor(model_path)

    module_name = f'.{model.name}.getinputs'
    module = importlib.import_module(module_name, 'prediction.models')

    features = module.get_inputs(generate_time_steps(start_time, hours))

    predictions = model.predict(features).flatten()
    points = [
        MeasurementPoint(timestamp=start_time + dt.timedelta(hours=i),
                         fields={'prediction': prediction}) for i, prediction in enumerate(predictions)
    ]
    return points


def predict_pv(sensor_name: str):
    model_path = get_model_path(sensor_name, 'models_pv')
    if not model_path.exists():
        raise FileNotFoundError

    model = load_model_for_sensor(model_path)

    db = database.get_db()
    mdi = db.meteoblue.find_one(sort=[('_id', -1)])

    assert mdi is not None, "No meteoblue prediction found"

    meteoblue_df = pd.DataFrame(mdi['data']['data_1h'])
    meteoblue_df = meteoblue_df[['time', 'ghi_instant']]

    def convert_to_utc(series):
        series = pd.to_datetime(series)
        series = series.dt.tz_localize('Europe/Vienna')
        return series.dt.tz_convert('utc')

    meteoblue_df['time'] = convert_to_utc(meteoblue_df['time'])
    meteoblue_df = meteoblue_df.set_index(['time'])

    lat = 47.058333
    lon = 15.459917
    solpos_df = solarposition.get_solarposition(meteoblue_df.index, lat, lon, altitude=300)

    meteoblue_df = meteoblue_df.join(solpos_df, how='outer')
    mb_features = [
        'ghi_instant',
        'zenith',
        'elevation',
        'azimuth',
        'apparent_zenith',
        'apparent_elevation'
    ]

    lookback = 0
    lookahead = 0

    features = meteoblue_df[mb_features].to_numpy()
    x_mb, _ = dm.processing.shape.get_windows(lookback, features, lookahead, np.zeros((features.shape[0], 1)))

    predictions = model.predict(x_mb).flatten()
    points = [
        MeasurementPoint(timestamp=timestamp, fields={'prediction': prediction})
        for timestamp, prediction in zip(meteoblue_df.index, predictions)
    ]

    return points
