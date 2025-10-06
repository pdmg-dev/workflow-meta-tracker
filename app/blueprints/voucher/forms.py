# app/blueprints/vouchers/forms.py

from datetime import datetime, timezone
from decimal import Decimal

from flask_wtf import FlaskForm
from wtforms import DecimalField, HiddenField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, NumberRange, Optional, Regexp, ValidationError

from app.blueprints.voucher.services import local_timezone
from app.extensions import db
from app.models.voucher import VoucherOrigin, VoucherType


class VoucherForm(FlaskForm):
    date_received = StringField("Date Received", validators=[InputRequired(message="Please pick the date received.")])
    voucher_type = SelectField("Type", coerce=int, validators=[InputRequired(message="Please select a voucher type.")])
    origin = StringField("Origin", validators=[Optional()])

    origin_id = HiddenField(
        "Origin ID",
        validators=[InputRequired(message="Please choose an origin.")],
        filters=[lambda x: int(x) if x and str(x).isdigit() else None],
    )

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
    amount = DecimalField(
        "Amount",
        places=2,
        rounding=None,
        filters=[lambda x: x.replace(",", "") if isinstance(x, str) else x],
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
        self.origins = db.session.query(VoucherOrigin).order_by(VoucherOrigin.code.asc()).all()

    def validate_date_received(self, field):
        try:
            naive = datetime.strptime(field.data, "%m/%d/%Y %I:%M %p")
        except ValueError as error:
            raise ValidationError("Invalid date format. Please use MM/DD/YYYY hh:mm AM/PM") from error

        local_dt = naive.replace(tzinfo=local_timezone)
        self.cleaned_date_received = local_dt.astimezone(timezone.utc)
        now_local = datetime.now(local_timezone)

        if local_dt > now_local:
            raise ValidationError("Date cannot be in the future.")

    def validate_origin(self, field):
        origin_input = (field.data or "").strip()

        # If JS already set origin_id, prefer it (avoid double work)
        if self.origin_id.data:
            origin_obj = VoucherOrigin.query.get(self.origin_id.data)
            if origin_obj:
                self.cleaned_origin = origin_obj
                return

        # Otherwise, fallback: try to resolve text input
        origin_obj = VoucherOrigin.query.filter(
            db.or_(
                VoucherOrigin.name.ilike(origin_input),
                VoucherOrigin.code.ilike(origin_input),
                VoucherOrigin.keyword.ilike(origin_input),
            )
        ).first()

        if origin_obj:
            self.cleaned_origin = origin_obj
            self.origin_id.data = origin_obj.id  # backfill hidden
            return

        raise ValidationError("Invalid origin. Please select an office by picking from the list.")
