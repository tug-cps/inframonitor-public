from admin.forms import BuildingForm
from .base import TypeView


class BuildingView(TypeView):
    type = 'Building'
    can_export = True
    can_delete = True
    can_create = True
    can_edit = True

    column_list = [
        '_id',
        'address.value.streetAddress',
        'refSite.object',
        'category.value'
    ]
    column_sortable_list = column_list
    column_searchable_list = column_list
    column_labels = {
        'address.value.streetAddress': 'Address',
        'refSite.object': 'Site',
        'category.value': 'Categories'
    }

    can_view_details = True
    column_details_list = [
        '_id',
        'type'
        'address',
        'category',
        'location',
        'refSite'
    ]

    form = BuildingForm

    def append_choices(self, form):
        buildings = [''] + [b['_id'] for b in self.coll.find({'type': 'Site'}, ['_id'])]
        form.refSite.object.choices = buildings
        return form

    def edit_form(self, obj):
        return self.append_choices(super().edit_form(obj))

    def create_form(self, obj=None):
        return self.append_choices(super().create_form(obj))

    def create_model(self, form):
        data = form.data

        return self.coll.insert_one({
            '_id': data['mongo_id'],
            'type': 'Building',
            'category': data['category'],
            'location': data['location'],
            'address': data['address']
        }).acknowledged

    def update_model(self, form, model):
        data = form.data

        if data['mongo_id'] != model['_id']:
            if not self.coll.insert_one({
                '_id': data['mongo_id'],
                'type': 'Building',
                'category': data['category'],
                'location': data['location'],
                'address': data['address'],
                'refSite': data['refSite']
            }).acknowledged:
                return False

            return self.coll.delete_one({'_id': model['_id']}).acknowledged

        self.coll.update_one(
            {'_id': data['mongo_id']},
            {'$set': {
                'category': data['category'],
                'location': data['location'],
                'address': data['address'],
                'refSite': data['refSite']
            }}
        )
        return True
