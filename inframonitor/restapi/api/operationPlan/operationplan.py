import json
import os

from flask import abort
from flask.views import MethodView
from paho.mqtt import publish
from pymongo.collection import Collection

from restapi.api_common import body_validate
from restapi.db import database
from restapi.model.schedule import Schedule
from restapi.schema.operation_plan import body_schema

MQTT_HOST = os.environ.get('MQTT_HOST', "localhost")


class OperationPlanView(MethodView):
    def __init__(self) -> None:
        super().__init__()
        db = database.get_db()
        self.coll: Collection = db.operationPlan

    def search(self):
        entry = self.coll.find_one(sort=[('_id', -1)])
        return Schedule.from_db(entry) if entry else abort(404)

    @body_validate(body_schema)
    def post(self, body):
        # FIXME restrict permissions / give users roles in jwt
        # FIXME make more dynamic / futureproof

        allowed_sensors = [
            'In1In21H922_S92__ber.SW_VL_Akt_Traj',
            'In1In21H922_S92_Y04_Akt_Traj',
            'In1In21H922_S92_Y05_Akt_Traj',
            'In1In21H922_S92_Y06_Akt_Traj',
            'In1In21H922_S92_Y07_Akt_Traj',
        ]

        for schedule in body['schedules']:
            if schedule['id'] not in allowed_sensors:
                abort(400, f'Setting trajectory for sensor {schedule["id"]} not allowed')

        topic = '/A8WKe1bv50bahwHWf5OtuqQc/In1In21/H922/datapointarrayobject/attrs'

        try:
            publish.single(topic, payload=json.dumps(body), hostname=MQTT_HOST)
        except Exception:
            abort(500, 'Failed to publish trajectory over MQTT')

        result = self.coll.insert_one(body)
        return ("", 201) if result.acknowledged else abort(507)
