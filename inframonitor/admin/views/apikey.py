from flask_jwt_extended import create_access_token

from admin.forms import ApiKeyForm
from admin.views.base import BaseView


class ApiKeyView(BaseView):
    can_delete = True
    can_create = True

    column_list = ['comment', 'apiKey']
    column_sortable_list = column_list
    column_searchable_list = column_list

    form = ApiKeyForm

    def create_model(self, form):
        data = form.data

        return self.coll.insert_one({
            'apiKey': create_access_token({}),
            'comment': data['comment']
        }).acknowledged
