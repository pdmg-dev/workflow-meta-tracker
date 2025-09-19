# app/blueprints/vouchers/forms.py

from datetime import datetime
from decimal import Decimal

import pytz
from flask_wtf import FlaskForm
from wtforms import (
    DateTimeLocalField,
    DecimalField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import InputRequired, Length, NumberRange, Regexp, ValidationError

from app.extensions import db
from app.models.voucher import VoucherType


class VoucherForm(FlaskForm):
    voucher_type = SelectField("Type", coerce=int, validators=[InputRequired(message="Please select a voucher type.")])
    payee = StringField(
        "Payee",
        validators=[
            InputRequired(message="Payee is required."),
            Regexp(
                regex=r"^[A-Za-z\s\-\.]+$", message="Payee name can only contain letters, spaces, hyphens, and periods."
            ),
            Length(max=120, message="Payee name is too long. Keep it under 120 characters."),
        ],
    )
    amount = DecimalField(
        "Amount",
        places=2,
        rounding=None,
        validators=[
            InputRequired(message="Amount is required."),
            NumberRange(min=Decimal("0.01"), message="Amount must be greater than 0."),
        ],
    )
    particulars = TextAreaField(
        "Particulars",
        validators=[
            InputRequired(message="Please describe the particulars."),
            Length(max=2000, message="Particulars too long (max 2000 chars)."),
        ],
    )
    origin = StringField(
        "Origin",
        validators=[
            InputRequired(message="Origin is required."),
            Length(max=120, message="Origin name is too long. Keep it under 120 characters."),
        ],
    )
    date_received = DateTimeLocalField(
        "Date Received",
        format="%Y-%m-%dT%H:%M",
        default=lambda: datetime.now(pytz.timezone("Asia/Manila")),
        validators=[InputRequired(message="Please pick the date received.")],
    )
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super(VoucherForm, self).__init__(*args, **kwargs)
        self.voucher_type.choices = [
            (vt.id, vt.name) for vt in db.session.query(VoucherType).order_by(VoucherType.name.asc()).all()
        ]

    def validate_date_received(self, field):
        PH_TZ = pytz.timezone("Asia/Manila")
        field_dt = PH_TZ.localize(field.data)
        now_ph = datetime.now(PH_TZ)
        if field_dt > now_ph:
            raise ValidationError("Date cannot be in the future.")
