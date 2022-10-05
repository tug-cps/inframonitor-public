from wtforms import form, fields


class BuildingForm(form.Form):
    class CategoriesForm(form.Form):
        type = fields.SelectField(choices=['Property'])
        value = fields.SelectMultipleField(choices=['office', 'lab', 'lecture hall'])

    class AddressForm(form.Form):
        class AddressValueForm(form.Form):
            addressLocality = fields.StringField('Address Locality', default='Graz')
            streetAddress = fields.StringField('Street Address')
            postalCode = fields.StringField('Postal Code')

        type = fields.SelectField(choices=['Property'])
        value = fields.FormField(AddressValueForm)

    class LocationForm(form.Form):
        class GeoLocationForm(form.Form):
            type = fields.SelectField(choices=['Point'])
            coordinates = fields.FieldList(fields.StringField(), min_entries=2)

        type = fields.SelectField(choices=['GeoProperty'])
        value = fields.FormField(GeoLocationForm)

    class RefSiteForm(form.Form):
        type = fields.SelectField(choices=['Relationship'])
        object = fields.SelectField()

    mongo_id = fields.StringField('id', default='urn:ngsi-ld:Building:')
    category = fields.FormField(CategoriesForm)
    address = fields.FormField(AddressForm)
    location = fields.FormField(LocationForm)
    refSite = fields.FormField(RefSiteForm)
