# app/blueprints/vouchers/__init__.py
from flask import Blueprint

voucher_bp = Blueprint("voucher", __name__)

from . import forms, views  # noqa: E402 F401
