import os
import shutil

from flask import render_template, url_for, redirect, flash, request
from NAS_Family import app, db, max_size, access_code
from NAS_Family.Models import User
from NAS_Family.Forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm, UploadImagesForm, EmailChangeForm, EmailVerificationForm, PasswordChangeForm, CSRF
from flask_login import login_user, logout_user, login_required, current_user
from NAS_Family.app_utils import password_reset_email, secure_password, save_images, load_images, delete_images, send_images, get_file_size, check_file, generate_secret


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    codes = access_code

    if form.validate_on_submit():
        access_verify = form.code.data
        code_use = User.query.filter_by(access_code=access_verify).first()
        email_user = User.query.filter_by(email=form.email.data).first()

        if not code_use and access_verify in codes:
            if form.email.data == 'phuocnhan18062001@gmail.com' or email_user:
                flash(f'Email already used', 'error')
            else:
                return redirect(url_for('verify_email', _external=True, _scheme='https', action='register', email=form.email.data, password=secure_password(form.password.data), access_code=access_verify, code=generate_secret(form.email.data)))
        else:
            flash(f'Invalid or Used Access Code', 'error')

    return render_template('register.html', form=form)


@app.route("/verify_email", methods=['GET', 'POST'])
def verify_email():
    form = EmailVerificationForm()
    old_email = ''
    email = request.args.get('email')
    action = request.args.get('action')
    code = request.args.get('code')
    print(code)

    if action == 'register':
        password = request.args.get('password')
        access_code = request.args.get('access_code')
    else:
        old_email = request.args.get('old_email')

    if form.validate_on_submit():
        if code == form.code.data:
            if action == 'register':
                new_user = User(email=email, password=password, access_code=access_code)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login', _external=True, _scheme='https'))
            else:
                if os.path.isdir(os.path.join(app.root_path, 'static\\Data\\User\\' + old_email)):
                    shutil.move(os.path.join(app.root_path, 'static\\Data\\User\\' + old_email), os.path.join(app.root_path, 'static\\Data\\User\\' + email))

                if os.path.isdir(os.path.join(app.root_path, 'static\\Data\\Display\\' + old_email)):
                    shutil.move(os.path.join(app.root_path, 'static\\Data\\Display\\' + old_email), os.path.join(app.root_path, 'static\\Data\\Display\\' + email))

                if os.path.isdir(os.path.join(app.root_path, 'static\\Data\\Zip\\' + old_email)):
                    shutil.move(os.path.join(app.root_path, 'static\\Data\\Zip\\' + old_email), os.path.join(app.root_path, 'static\\Data\\Zip\\' + email))

                user = User.query.filter_by(email=old_email).first()
                user.email = email
                db.session.commit()
                return redirect(url_for('home', _external=True, _scheme='https'))
        else:
            flash(f'Invalid Code', 'error')

    return render_template('verify_email.html', form=form)


@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        password = secure_password(form.password.data)

        if user and password == user.password:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home', _external=True, _scheme='https'))
        else:
            flash(f'Typos Spotted', 'error')

    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login', _external=True, _scheme='https'))


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        password_reset_email(user)
        flash('Top-secret instruction was sent to your email')
        return redirect(url_for('login', _external=True, _scheme='https'))

    return render_template('reset_request.html', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_reset_token(token)

    if user is None:
        flash('Are you authorized to handle top-secrets?', 'warning')
        return redirect(url_for('reset_request', _external=True, _scheme='https'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        user.password = secure_password(form.password.data)
        db.session.commit()
        flash('Password Updated')
        return redirect(url_for('login', _external=True, _scheme='https'))
    return render_template('reset_token.html', form=form)


@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    form = CSRF()
    img_path = load_images(current_user.email, True)

    if request.method == 'POST':
        os.remove(app.root_path + '\\static\\' + request.form['id'])
        os.remove(app.root_path + '\\static\\Data\\User' + request.form['id'].split('Display')[1])
        return redirect(url_for('home', _external=True, _scheme='https'))

    return render_template('home.html', path=img_path, form=form)


@app.route("/home/change_email", methods=['GET', 'POST'])
@login_required
def change_email():
    form = EmailChangeForm()

    if form.validate_on_submit():
        if check_file(form.new_email.data) and form.email.data != 'phuocnhan18062001@gmail.com':
            user = User.query.filter_by(email=form.email.data).first()

            if user.email == form.email.data:
                return redirect(url_for('verify_email', _external=True, _scheme='https', action='change', email=form.new_email.data, old_email=user.email, code=generate_secret(form.new_email.data)))
            else:
                flash(f'Failed to Verify Email', 'error')
        else:
            flash(f'Email Existed', 'error')

    return render_template('change_email.html', form=form)


@app.route("/home/change_password", methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordChangeForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()

        if secure_password(form.old_password.data) == user.password:
            user.password = secure_password(form.password.data)
            db.session.commit()
            return redirect(url_for('home', _external=True, _scheme='https'))
        else:
            flash(f'Invalid Password', 'error')

    return render_template('change_password.html', form=form)


@app.route("/home/upload_images", methods=['GET', 'POST'])
@login_required
def upload_images():
    form = UploadImagesForm()

    if form.validate_on_submit():
        size = get_file_size(form.images.data, current_user.email)

        if size < max_size:
            save_images(form.images.data, current_user.email)
            return redirect(url_for('home', _external=True, _scheme='https'))
        else:
            flash(f'You reach the maximum storage capacity', 'error')

    return render_template('upload_images.html', form=form)


@app.route("/home/download_images", methods=['GET', 'POST'])
@login_required
def download_images():
    if os.path.isdir(os.path.join(app.root_path, 'static\\Data\\User\\' + current_user.email)):
        send_images(current_user.email)
    else:
        flash(f'Please upload images first', 'error')

    return redirect(url_for('home', _external=True, _scheme='https'))


@app.route("/home/clear_images", methods=['GET', 'POST'])
@login_required
def clear_images():
    delete_images(current_user.email)
    return redirect(url_for('home', _external=True, _scheme='https'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
