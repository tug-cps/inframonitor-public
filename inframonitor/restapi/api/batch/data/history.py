from flask.views import MethodView

from restapi.api.batch.data.common import query_field
from restapi.model.paged_data import PagedData


class HistoryView(MethodView):
    def search(self, data_item_ids: str, from_: int = None, to: int = None, limit: int = None, offset: int = 0,
               order: str = 'ASC', sample_time: int = None, aggregation: str = 'first', fill: str = 'null'):
        data_items, values = query_field(data_item_ids, 'reading', from_, to, limit, offset, order, sample_time,
                                         aggregation, fill)

        return {
            'metadata': PagedData(limit or -1, offset or 0, order, len(values)),
            'ids': data_items,
            'values': values
        }
