from wtforms import form, fields


class SiteForm(form.Form):
    mongo_id = fields.StringField('id', default='urn:ngsi-ld:Site:')
    name = fields.StringField()
