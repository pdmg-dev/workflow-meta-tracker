# app/blueprints/vouchers/forms.py

from datetime import datetime, timezone
from decimal import Decimal

import pytz
from flask_wtf import FlaskForm
from wtforms import (
    DecimalField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import InputRequired, Length, NumberRange, Regexp, ValidationError

from app.extensions import db
from app.models.voucher import VoucherOrigin, VoucherType


class VoucherForm(FlaskForm):
    voucher_type = SelectField("Type", coerce=int, validators=[InputRequired(message="Please select a voucher type.")])
    origin = SelectField("Origin", coerce=int, validators=[InputRequired(message="Please select an origin.")])
    date_received = StringField("Date Received", validators=[InputRequired(message="Please pick the date received.")])

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
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super(VoucherForm, self).__init__(*args, **kwargs)
        self.voucher_type.choices = [
            (vt.id, vt.name) for vt in db.session.query(VoucherType).order_by(VoucherType.name.asc()).all()
        ]
        self.origin.choices = [
            (o.id, o.code) for o in db.session.query(VoucherOrigin).order_by(VoucherOrigin.code.asc()).all()
        ]

    def validate_date_received(self, field):
        try:
            naive_local = datetime.strptime(field.data, "%Y-%m-%d %I:%M %p")
        except ValueError as error:
            raise ValidationError("Invalid date format.") from error

        ph_tz = pytz.timezone("Asia/Manila")
        aware_local = ph_tz.localize(naive_local)
        if aware_local > datetime.now(ph_tz):
            raise ValidationError("Date cannot be in the future.")
        field.data = aware_local.astimezone(timezone.utc)
