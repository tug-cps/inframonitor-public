from flask import abort
from flask.views import MethodView
from pymongo.collection import Collection

from restapi.db import database
from restapi.model.building import Building


class BuildingView(MethodView):

    def __init__(self) -> None:
        super().__init__()
        self.db = database.get_db()

    def search(self, site_id=None):
        coll: Collection = self.db.entities

        if site_id:
            match = {"$match": {"type": "Building", "refSite.object": site_id}}
        else:
            match = {"$match": {"type": "Building"}}

        query = coll.aggregate([
            match,
            {"$lookup": {
                "from": "entities",
                "localField": "_id",
                "foreignField": "refBuilding.object",
                "as": "dataItemIds"
            }}
        ])

        entries = list(query)
        return [Building.from_db(entry) for entry in entries]

    def get(self, building_id):
        assert type(building_id) is str

        coll: Collection = self.db.entities
        try:
            query = coll.aggregate([
                {"$match": {"type": "Building", "_id": building_id}},
                {"$lookup": {
                    "from": "entities",
                    "localField": "_id",
                    "foreignField": "refBuilding.object",
                    "as": "dataItemIds"
                }}
            ])
            item = query.next()
            return Building.from_db(item)
        except StopIteration:
            abort(404)
