from wtforms import form, fields


class ApiKeyForm(form.Form):
    comment = fields.StringField('comment')
