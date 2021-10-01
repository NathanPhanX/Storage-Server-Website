from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from flask_wtf.file import FileAllowed
from NAS_Family.Models import User


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message='Invalid Email')])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=40)])
    password_conf = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Unmatched Password')])
    code = StringField('Access Code', validators=[DataRequired()])
    security = RecaptchaField()
    submit = SubmitField('Register')

    # This method is override so do not change the name
    def validate_email(self, user_email):
        user = User.query.filter_by(email=user_email.data).first()

        if user:
            raise ValidationError('Email is already registered')


class EmailVerificationForm(FlaskForm):
    code = StringField('Code', validators=[DataRequired()])
    security = RecaptchaField()
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message='Invalid Email')])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=20)])
    security = RecaptchaField()
    submit = SubmitField('Login')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message='Invalid Email')])
    security = RecaptchaField()
    submit = SubmitField('Request Password Change')

    # This method is override so do not change the name
    def validate_email(self, user_email):
        user = User.query.filter_by(email=user_email.data).first()

        if user is None:
            raise ValidationError('There is no account with the email')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=20)])
    password_conf = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Unmatched Password')])
    security = RecaptchaField()
    submit = SubmitField('Change Password')


class UploadImagesForm(FlaskForm):
    images = MultipleFileField('Choose Files', validators=[DataRequired(), FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Upload Images')


class EmailChangeForm(FlaskForm):
    email = StringField('Old Email', validators=[DataRequired(), Email(message='Invalid Email')])
    new_email = StringField('New Email', validators=[DataRequired(), Email(message='Invalid Email')])
    security = RecaptchaField()
    submit = SubmitField('Change Email')

    # This method is override so do not change the name
    def validate_email(self, user_email):
        user = User.query.filter_by(email=user_email.data).first()

        if user is None:
            raise ValidationError('There is no account with the email')


class PasswordChangeForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=4, max=20)])
    password_conf = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Unmatched Password')])
    security = RecaptchaField()
    submit = SubmitField('Change Password')


class CSRF(FlaskForm):
    submit = SubmitField('')
