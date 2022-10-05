import datetime as dt

from flask import abort
from flask.views import MethodView

from restapi.db import database
from restapi.model.weather_forecast_data import WeatherForecastData


class ForecastView(MethodView):
    def search(self, from_: int = None, to: int = None):
        db = database.get_db()

        query = {'timestamp': {}} if from_ or to else {}
        if from_:
            query['timestamp']['$gt'] = dt.datetime.fromtimestamp(from_, tz=dt.timezone.utc) - dt.timedelta(seconds=1)
        if to:
            query['timestamp']['$lt'] = dt.datetime.fromtimestamp(to, tz=dt.timezone.utc) + dt.timedelta(seconds=1)

        entries = db.meteoblue.find(query, projection={'timestamp': 1}) or abort(404)
        entries = list(entries)
        return [{
            'created': int(entry['timestamp'].replace(tzinfo=dt.timezone.utc).timestamp()),
        } for entry in entries]

    def get(self, created: int, from_: int = None, to: int = None):
        db = database.get_db()

        if created == -1:
            entry = db.meteoblue.find_one(sort=[('_id', -1)]) or abort(404)
        else:
            _from = dt.datetime.fromtimestamp(created, tz=dt.timezone.utc)
            _to = _from + dt.timedelta(seconds=1)
            entry = db.meteoblue.find_one({'timestamp': {'$gte': _from, '$lte': _to}}) or abort(404)

        return WeatherForecastData.from_db(entry, from_, to)
