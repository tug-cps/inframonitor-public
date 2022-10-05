import os

from flask import Flask, redirect, url_for
from flask_admin import Admin, expose, AdminIndexView
from flask_jwt_extended import JWTManager

from admin.views import BuildingView, SensorView
from admin.views.apikey import ApiKeyView
from admin.views.site import SiteView
from common import database

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', '123456790')
app.config['FLASK_ADMIN_SWATCH'] = 'cosmo'
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", None)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
app.config["JWT_TOKEN_LOCATIONS"] = ['headers']
JWTManager(app)

entities = database.get_db().entities
protected_db = database.get_protected_db()


class DashBoardView(AdminIndexView):
    @expose('/')
    def index(self):
        type_array = {e['_id']: e['count'] for e in entities.aggregate(
            [{'$group': {'_id': '$type', 'count': {'$count': {}}}}])}
        sites = type_array['Site']
        buildings = type_array['Building']
        sensors = sum(e[1] for e in type_array.items() if e[0] != 'Building' and e[0] != 'Site')
        return self.render('admin/index.html', sites=sites, buildings=buildings, sensors=sensors)


@app.route('/')
def index():
    return redirect(url_for('admin.index'))


@app.route('/chart/data/')
def chart_data():
    sites = list(entities.find({'type': 'Site'}))
    buildings = list(entities.find({'type': 'Building'}))
    sensors = list(entities.find({'type': {'$nin': ['Site', 'Building']}}))
    return {
        'nodes':
            ([{'id': item['_id'], 'fill': '#ff00ff'} for item in sites]
             + [{'id': item['_id'], 'fill': '#00ff00'} for item in buildings]
             + [{'id': item['_id']} for item in sensors if item.get('refBuilding', {}).get('object')]),
        'edges':
            ([{'from': item['_id'], 'to': item['refSite']['object']} for item in buildings]
             + [{'from': item['_id'], 'to': item['refBuilding']['object']} for item in sensors if
                item.get('refBuilding', {}).get('object')])
    }


admin = Admin(app, name='inframonitor admin', template_mode='bootstrap2', index_view=DashBoardView())

admin.add_view(SiteView(entities, name='Sites'))
admin.add_view(BuildingView(entities, name='Buildings'))
admin.add_view(SensorView(entities, name='Sensors'))
admin.add_view(ApiKeyView(protected_db.apikey, name='ApiKeys'))

if __name__ == "__main__":
    app.run(debug=True)
