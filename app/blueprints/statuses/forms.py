# app/blueprints/statuses/forms.py
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired

from app.extensions import db

from .models import Status

# TODO: Create StatusForm for status creation


class StatusUpdateForm(FlaskForm):
    status = SelectField("Status", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Update")

    def __init__(self, *args, **kwargs):
        super(StatusUpdateForm, self).__init__(*args, **kwargs)
        self.status.choices = [
            (status.id, status.name)
            for status in db.session.query(Status)
            .filter_by(is_active=True)
            .order_by(Status.name.asc())
            .all()
        ]
