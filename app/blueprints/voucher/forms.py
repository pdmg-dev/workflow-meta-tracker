# app/blueprints/vouchers/forms.py

from datetime import datetime, timezone
from decimal import Decimal

from flask_wtf import FlaskForm
from wtforms import (
    DecimalField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import InputRequired, Length, NumberRange, Regexp, ValidationError

from app.blueprints.voucher.services import local_timezone, parse_local_datetime
from app.extensions import db
from app.models.voucher import VoucherFund, VoucherOrigin, VoucherType


class VoucherForm(FlaskForm):
    voucher_type = SelectField("Type", coerce=int, validators=[InputRequired(message="Please select a voucher type.")])
    fund = StringField("Fund", validators=[InputRequired(message="Please select fund.")])
    date_received = StringField("Date Received", validators=[InputRequired(message="Please pick the date received.")])

    payee = StringField(
        "Payee",
        validators=[
            InputRequired(message="Payee is required."),
            Regexp(
                regex=r"^[A-Za-z\s\-\.&]+$",
                message="Payee name can only contain letters, spaces, hyphens, and periods.",
            ),
            Length(max=120, message="Payee name is too long. Keep it under 120 characters."),
        ],
    )
    origin = StringField("Origin", validators=[InputRequired(message="Origin must be an office or code")])

    address = StringField(
        "Address",
        validators=[
            InputRequired(message="Address is required."),
            Regexp(
                regex=r"^[A-Za-z0-9\s\.,#/\-]+$",
                message="Address name can only contain letters, spaces, hyphens, and periods.",
            ),
            Length(max=120, message="Address is too long. Keep it under 120 characters."),
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
        "Explanation",
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

    def validate_date_received(self, field):
        try:
            aware_local = parse_local_datetime(field.data)
        except ValueError as error:
            raise ValidationError(str(error)) from error

        if aware_local > datetime.now(local_timezone):
            raise ValidationError("Date cannot be in the future.")
        self.cleaned_date_received = aware_local.astimezone(timezone.utc)

    def validate_fund(self, field):
        fund_input = field.data.strip()

        fund = VoucherFund.query.filter(
            db.or_(VoucherFund.name.ilike(fund_input), VoucherFund.code.ilike(fund_input))
        ).first()

        if not fund:
            raise ValidationError("Invalid fund. Please enter a valid fund name or code.")
        self.cleaned_fund = fund

    def validate_origin(self, field):
        origin_input = field.data.strip()

        origin = VoucherOrigin.query.filter(
            db.or_(VoucherOrigin.name.ilike(origin_input), VoucherOrigin.code.ilike(origin_input))
        ).first()

        if not origin:
            raise ValidationError("Invalid origin. Please enter a valid office name or code.")
        self.cleaned_origin = origin
