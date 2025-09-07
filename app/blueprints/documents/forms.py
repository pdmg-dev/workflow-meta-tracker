# app/blueprints/documents/forms.py
from datetime import date

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    FloatField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Optional

from app.extensions import db

from .models import DocumentType


class DocumentForm(FlaskForm):
    document_type = SelectField("Type", coerce=int)
    document_number = StringField("Document No.", validators=[Optional()])
    payee = StringField("Payee", validators=[DataRequired()])
    origin = StringField("Origin", validators=[DataRequired()])
    particulars = TextAreaField("Particulars", validators=[Optional()])
    amount = FloatField("Amount", validators=[Optional()])
    date_received = DateField(
        "Date Received", default=date.today, validators=[DataRequired()]
    )
    # status_id = SelectField("Status", coerce=int)
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
        self.document_type.choices = [
            (doc_type.id, doc_type.name)
            for doc_type in db.session.query(DocumentType)
            .filter_by(is_active=True)
            .order_by(DocumentType.name.asc())
            .all()
        ]

    # self.status_id.choices = [(s.id, s.name)
    # for s in Status.query.filter_by(is_active=True)]
