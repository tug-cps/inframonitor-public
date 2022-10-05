import datetime as dt

from flask_admin.contrib.pymongo.filters import FilterEqual, FilterLike, FilterNotEqual, FilterNotLike

from admin.forms import SensorForm
from .base import BaseView


class SensorView(BaseView):
    column_list = [
        '_id',
        'type',
        'name',
        'nameEnergo',
        'refProject',
        'description',
        'refBuilding.object',
        'source',
        'dateModified.value',
        'dateCreated.value',
    ]
    column_sortable_list = column_list
    column_searchable_list = column_list
    column_labels = {
        'dateModified.value': 'Last modified',
        'dateCreated.value': 'Created',
        'refBuilding.object': 'Building'
    }
    column_filters = (
        FilterEqual(column='type', name='Type'),
        FilterLike(column='type', name='Type'),
        FilterNotEqual(column='type', name='Type'),
        FilterLike(column='name', name='Name'),
        FilterNotLike(column='name', name='Name'),
        FilterEqual(column='source', name='Source'),
        FilterNotEqual(column='source', name='Source'),
        FilterEqual(column='refBuilding.object', name='Building'),
        FilterLike(column='refBuilding.object', name='Building'),
    )

    form = SensorForm

    can_export = True
    can_delete = True
    can_create = True
    can_edit = True
    page_size = 30

    can_view_details = True
    column_details_list = [
        '_id',
        'name',
        'description',
        'reading',
        'minPrediction',
        'maxPrediction',
        'dateCreated',
        'dateModified',
        'refBuilding',
        'source',
        'type',
        'refProject',
        'nameEnergo'
    ]

    def append_choices(self, form):
        buildings = [''] + [b['_id'] for b in self.coll.find({'type': 'Building'}, ['_id'])]
        form.refBuilding.object.choices = buildings
        return form

    def edit_form(self, obj):
        return self.append_choices(super().edit_form(obj))

    def create_form(self, obj=None):
        return self.append_choices(super().create_form(obj))

    def create_model(self, form):
        data = form.data
        return self.coll.insert_one({
            '_id': data['mongo_id'],
            'type': data['type'],
            'name': data['name'],
            'description': data['description'],
            'refBuilding': data['refBuilding'],
            'dateCreated': {
                'type': 'DateTime',
                'value': dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
            }
        }).acknowledged

    def update_model(self, form, model):
        data = form.data
        prev_id = model['_id']

        if data['mongo_id'] != prev_id:
            model.pop('mongo_id')
            model['_id'] = data['mongo_id']

            if not self.coll.insert_one(model).acknowledged:
                return False

            if not self.coll.delete_one({'_id': prev_id}).acknowledged:
                return False

        entries = ['type', 'name', 'description', 'refBuilding', 'refProject', 'nameEnergo']
        self.coll.update_one(
            {'_id': data['mongo_id']},
            {'$set': {e: data[e] for e in entries}}
        )
        return True

    def create_query(self, filters, search):
        return {
            "$and": [
                super().create_query(filters, search),
                {'type': {'$nin': ['Building', 'Site']}}
            ]
        }
