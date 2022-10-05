from flask import abort
from flask.views import MethodView

from restapi.api.dataItem.data.common import field_search
from restapi.model.paged_data import PagedData
from restapi.model.time_value_pair import TimeValuePair


class HistoryView(MethodView):
    def search(self, data_item_id: str, from_: int = None, to: int = None, limit: int = None, order: str = 'ASC',
               offset: int = None, sample_time: int = None, aggregation: str = 'first', fill: str = 'null'):
        if not from_ and not to and not limit:
            abort(400, "Either a 'from'- and 'to'- or a 'limit'-parameter must be provided!")

        field = 'reading'
        points = field_search(field, data_item_id, from_, to, limit, order, offset, sample_time, aggregation, fill)

        return {
            'metadata': PagedData(limit or -1, offset or 0, order, len(points)),
            'dataItemId': data_item_id,
            'dataItemValues': [TimeValuePair.from_db(p, field) for p in points]
        }
