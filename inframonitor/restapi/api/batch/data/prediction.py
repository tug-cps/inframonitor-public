from flask import abort
from flask.views import MethodView

from restapi.api.batch.data.common import query_field
from restapi.api_common import body_validate
from restapi.db import database
from restapi.model.paged_data import PagedData
from restapi.schema.batch_prediction_put import body_schema


class PredictionView(MethodView):
    def search(self, data_item_ids: str, from_: int = None, to: int = None,
               limit: int = None, offset: int = 0, order: str = 'ASC'):
        data_items, values = query_field(data_item_ids, 'prediction', from_, to, limit, offset, order)

        return {
            'metadata': PagedData(limit or -1, offset or 0, order, len(values)),
            'ids': data_items,
            'values': values,
            'created': -1
        }

    @body_validate(body_schema)
    def post(self, body):

        ids = body["ids"]
        timevaluespair = body["values"]
        created = body["created"]

        if len(timevaluespair) == 0:
            abort(400)

        if len(ids) != len(timevaluespair[0]['values']):
            abort(400)

        tsdb = database.get_tsdb()
        db = database.get_db()

        names = []
        for sensor_id in ids:
            sensor = db.entities.find_one({"_id": sensor_id})
            if sensor is None:
                abort(404)
            names.append(sensor["name"])

        influx_points = []
        for predictions in timevaluespair:
            for (name, value) in zip(names, predictions['values']):
                influx_points.append({
                    'measurement': 'sensor-readings',  # FIXME
                    'time': predictions['timestamp'],
                    'fields': {'prediction': value},
                    'tags': {'sensor': name, 'created': created}
                })

        tsdb.write_points(influx_points, time_precision='s')
        return {}, 201
