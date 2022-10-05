from flask.views import MethodView
from pymongo.collection import Collection
from werkzeug.exceptions import abort

from common.type_def import building_types
from restapi.db import database
from restapi.model.dataitem import DataItem


class DataItemView(MethodView):

    def __init__(self) -> None:
        super().__init__()
        self.db = database.get_db()

    def search(self, site_id=None, building_id=None):
        coll: Collection = self.db.entities
        query = {'$match': {'type': {'$nin': building_types}}}

        if building_id:
            query['$match']['refBuilding.object'] = building_id
        elif site_id:
            buildings = list(coll.find({"refSite.object": site_id, "type": "Building"})) or abort(404)
            query['$match']['refBuilding.object'] = {"$in": buildings}

        query = coll.aggregate([query])
        return [DataItem.from_db(i) for i in query]

    def get(self, data_item_id):
        assert type(data_item_id) is str

        coll: Collection = self.db.entities
        entry = coll.find_one({"type": {"$nin": building_types}, "_id": data_item_id}) or abort(404)

        return DataItem.from_db(entry)
