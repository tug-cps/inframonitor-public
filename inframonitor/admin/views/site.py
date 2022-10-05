from admin.forms import SiteForm
from .base import TypeView


class SiteView(TypeView):
    can_export = True
    can_delete = True
    can_create = True
    can_edit = True

    type = 'Site'

    column_list = [
        '_id',
        'name'
    ]
    column_sortable_list = column_list
    column_searchable_list = column_list

    form = SiteForm

    def create_model(self, form):
        data = form.data

        return self.coll.insert_one({
            '_id': data['mongo_id'],
            'type': 'Site',
            'name': data['name']
        }).acknowledged

    def update_model(self, form, model):
        data = form.data

        return self.coll.update_one(
            {'_id': model['_id'], 'type': 'Site'},
            {'$set': {'name': data['name']}}
        ).acknowledged
