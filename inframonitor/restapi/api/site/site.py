from flask import abort
from flask.views import MethodView
from pymongo.collection import Collection

from restapi.db import database
from restapi.model.site import Site


class SiteView(MethodView):

    def search(self):
        db = database.get_db()
        coll: Collection = db.entities
        query = coll.aggregate([
            {'$match': {'type': 'Site'}},
            {'$lookup': {
                'from': 'entities',
                'localField': '_id',
                'foreignField': 'refSite.object',
                'as': 'buildingIds'
            }}
        ])
        entries = list(query)
        return [Site.from_db(entry) for entry in entries]

    def get(self, site_id):
        db = database.get_db()
        coll: Collection = db.entities
        query = coll.aggregate([
            {'$match': {'type': 'Site', '_id': site_id}},
            {'$lookup': {
                'from': 'entities',
                'localField': '_id',
                'foreignField': 'refSite.object',
                'as': 'buildingIds'
            }}
        ])
        try:
            item = query.next()
            return Site.from_db(item)
        except StopIteration:
            abort(404)
