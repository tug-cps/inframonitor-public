import pymongo
from flask import flash
from flask_admin.babel import gettext
from flask_admin.contrib.pymongo import ModelView
from flask_admin.contrib.pymongo.view import log


class BaseView(ModelView):
    def __init__(self, coll, name=None, category=None, endpoint=None, url=None, menu_class_name=None,
                 menu_icon_type=None, menu_icon_value=None):
        if not endpoint:
            endpoint = ('%sview' % name).lower()

        super().__init__(coll, name, category, endpoint, url, menu_class_name, menu_icon_type, menu_icon_value)

    def _get_field_value(self, model, name):
        a, *b = name.split('.')
        value = model.get(a)
        for i in b:
            value = value.get(i) if value else None
        return value

    def create_query(self, filters, search):
        query = {}
        # Filters
        if self._filters:
            data = []

            for flt, flt_name, value in filters:
                f = self._filters[flt]
                data = f.apply(data, f.clean(value))

            if data:
                if len(data) == 1:
                    query = data[0]
                else:
                    query['$and'] = data

        # Search
        if self._search_supported and search:
            query = self._search(query, search)
        return query

    def get_one(self, id):
        result = super().get_one(id)
        result['mongo_id'] = result['_id']
        return result

    def get_list(self, page, sort_column, sort_desc, search, filters, execute=True, page_size=None):
        query = self.create_query(filters, search)

        # Get count
        count = self.coll.count_documents(query) if not self.simple_list_pager else None

        # Sorting
        sort_by = None

        if sort_column:
            sort_by = [(sort_column, pymongo.DESCENDING if sort_desc else pymongo.ASCENDING)]
        else:
            order = self._get_default_order()

            if order:
                sort_by = [(col, pymongo.DESCENDING if desc else pymongo.ASCENDING)
                           for (col, desc) in order]

        # Pagination
        if page_size is None:
            page_size = self.page_size

        skip = 0

        if page and page_size:
            skip = page * page_size

        results = self.coll.find(query, sort=sort_by, skip=skip, limit=page_size)

        if execute:
            results = list(results)

        return count, results

    def delete_model(self, model):
        """
            Delete model helper

            :param model:
                Model instance
        """
        try:
            pk = self.get_pk_value(model)

            if not pk:
                raise ValueError('Document does not have _id')

            self.on_model_delete(model)
            self.coll.delete_one({'_id': pk})
        except Exception as ex:
            flash(gettext('Failed to delete record. %(error)s', error=str(ex)), 'error')
            log.exception('Failed to delete record.')
            return False
        else:
            self.after_model_delete(model)

        return True


class TypeView(BaseView):
    type = None

    def __init__(self, coll, name=None, category=None, endpoint=None, url=None, menu_class_name=None,
                 menu_icon_type=None, menu_icon_value=None):
        assert self.type is not None
        super().__init__(coll, name, category, endpoint, url, menu_class_name, menu_icon_type, menu_icon_value)

    def create_query(self, filters, search):
        return {
            "$and": [
                super().create_query(filters, search),
                {'type': self.type}
            ]
        }
