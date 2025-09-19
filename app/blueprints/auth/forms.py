from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired("Please enter your username."),
            Length(min=3, max=50, message="Username must be between 3 and 50 characters."),
        ],
        render_kw={"placeholder": "Username", "autocomplete": "username"},
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired("Please enter your password."),
            Length(max=128, message="Password must be at least 6 characters."),  # NOTE: add params 'min=6'
        ],
        render_kw={"placeholder": "Password", "autocomplete": "current-password"},
    )

    remember = BooleanField("Remember me")
    submit = SubmitField("Login")
