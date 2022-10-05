from flask import abort
from flask.views import MethodView

from restapi.api.dataItem.data.common import find_sensor, create_query, query_tsdb, create_points, write_tsdb
from restapi.api_common import body_validate
from restapi.model.paged_data import PagedData
from restapi.model.time_value_pair import TimeValuePair
from restapi.schema.data_accounting_put import body_schema


class AccountingView(MethodView):
    def search(self, data_item_id: str, from_: int = None, to: int = None,
               limit: int = None, order: str = 'ASC', offset: int = None):
        if not from_ and not to and not limit:
            abort(400, "Either a 'from'- and 'to'- or a 'limit'-parameter must be provided!")
        field = 'accounting'
        sensor = find_sensor(data_item_id)

        sensor.get('isAccountingSensor') or abort(400, 'Sensor is not an accounting sensor')
        sensor_name = sensor.get('name') or abort(404)
        query = create_query(field, from_, limit, offset, order, to)
        points = query_tsdb(query, sensor_name)

        return {
            'metadata': PagedData(limit or -1, offset or 0, order, len(points)),
            'dataItemId': data_item_id,
            'dataItemValues': [TimeValuePair.from_db(p, field) for p in points]
        }

    @body_validate(body_schema)
    def post(self, data_item_id: str, body):
        (values, created) = (body[idx] for idx in ['dataItemValues', 'created'])

        if not values:
            abort(400, "Values array is empty")

        sensor = find_sensor(data_item_id)
        sensor.get('isAccountingSensor') or abort(400, 'Sensor is not an accounting sensor')
        sensor_name = sensor.get('name') or abort(404, 'Sensor is invalid')

        influx_points = create_points(sensor_name, 'accounting', values, created)
        write_tsdb(influx_points)
        return {}, 201
