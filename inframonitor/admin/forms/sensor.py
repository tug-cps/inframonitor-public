from wtforms import form, fields


class SensorForm(form.Form):
    class RefBuildingForm(form.Form):
        type = fields.SelectField(choices=['Relationship'])
        object = fields.SelectField()

    mongo_id = fields.StringField('_id', default='urn:ngsi-ld:UnknownSensor:')
    type = fields.StringField(default='UnknownSensor')
    name = fields.StringField()
    nameEnergo = fields.StringField()
    description = fields.StringField()
    refBuilding = fields.FormField(RefBuildingForm)
    refProject = fields.StringField()
