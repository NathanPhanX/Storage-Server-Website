import smtplib
import secrets
import random
import shutil
import glob
import sys
import os

from flask import url_for
from NAS_Family import mail, app
from flask_mail import Message
from PIL import Image

from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase


def password_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@cloudstorage.com', recipients=[user.email])
    msg.body = f'''
    To reset the password, visit the following link:
    {url_for('reset_token', token=token, _external=True, _scheme='https')}
    If you did not make this request, ignore this email.
    '''

    mail.send(msg)


def generate_secret(user_email):
    code = str(secrets.token_hex(16))

    msg = Message('Email Verification', sender='noreply@cloudstorage.com', recipients=[user_email])
    msg.body = f'''
        Enter the code below to verify your email.
        {code}
        If you did not make this request, ignore this email.
        '''

    mail.send(msg)
    return code


def secure_password(pw):
    random.seed(len(pw))
    num = random.randint(0, 10)
    pw1 = ' '.join(format(ord(x), 'b') for x in pw).split(' ')
    pw2 = ''
    pw4 = ''
    pw6 = ''

    for data in pw1:
        num1 = num % len(data)
        pw2 += data[num1:] + data[: num1] + ' '

    pw3 = pw2.split(' ')[:-1]

    for data in pw3:
        num2 = str(bin(random.randint(2**(len(data) - 1), 2**len(data) - 1))[2:])
        pw4 += '1'

        for (x, y) in zip(data, num2):
            pw4 += str(int(x) ^ int(y))

        pw4 += ' '

    pw4 = pw4[:-1]
    num3 = len(pw)  # Change this random.randint(0, len(pw4)) for more secure if needed

    pw5 = pw4[num3:] + pw4[: num3]
    pw5 = '1' + pw5 + '0'
    pw5 = pw5.split(' ')

    for data in pw5:
        pw6 += str(int(data, 2)) + '-'

    secure_pw = pw6 + str(len(pw))
    return secure_pw


def save_images(images, user):
    if not os.path.isdir(os.path.join(app.root_path, 'static\\Data\\User\\' + user)):
        os.mkdir(os.path.join(app.root_path, 'static\\Data\\User\\' + user))

    if not os.path.isdir(os.path.join(app.root_path, 'static\\Data\\Display\\' + user)):
        os.mkdir(os.path.join(app.root_path, 'static\\Data\\Display\\' + user))

    for image in images:
        random_hex = secrets.token_hex(8)
        f_name, f_ext = os.path.splitext(image.filename)
        image_name = f_name + '@' + random_hex + f_ext
        image_dir = os.path.join(app.root_path, 'static\\Data\\User\\' + user, image_name)
        image.save(image_dir)

        display_img = Image.open(image_dir)
        display_img = display_img.resize((150, 150), Image.ANTIALIAS)
        display_img.save(os.path.join(app.root_path, 'static\\Data\\Display\\' + user, image_name))


def load_images(user, origin_path):
    img_per_column = 5

    if os.path.isdir(os.path.join(app.root_path, 'static\\Data\\User\\' + user)):
        img_path = []
        final_path = []
        count = 0
        path = glob.glob(app.root_path + '\\static\\Data\\User\\' + user + '\\*')

        for sub_path in path:
            if origin_path:
                img_path.append('Data\\Display\\' + user + sub_path.split(user)[1])
            else:
                img_path.append('static\\Data\\User\\' + user + sub_path.split(user)[1])

        row = int(len(img_path) / img_per_column) + 1

        for i in range(row):
            sub_img_path = []

            for j in range(img_per_column):
                sub_img_path.append(img_path[count])
                count += 1

                if count >= len(img_path):
                    final_path.append(sub_img_path)
                    return final_path

            final_path.append(sub_img_path)

        return final_path
    else:
        return []


def delete_images(user):
    if os.path.isdir(os.path.join(app.root_path, 'static\\Data\\User\\' + user)):
        shutil.rmtree(os.path.join(app.root_path, 'static\\Data\\User\\' + user))

    if os.path.isdir(os.path.join(app.root_path, 'static\\Data\\Display\\' + user)):
        shutil.rmtree(os.path.join(app.root_path, 'static\\Data\\Display\\' + user))


def send_images(user):
    if not os.path.isdir(os.path.join(app.root_path, 'static\\Data\\Zip\\' + user)):
        os.mkdir(os.path.join(app.root_path, 'static\\Data\\Zip\\' + user))

    if not os.path.isdir(os.path.join(app.root_path, 'static\\Data\\Zip\\', user, 'temp')):
        os.mkdir(os.path.join(app.root_path, 'static\\Data\\Zip\\', user, 'temp'))
    img_path = load_images(user, False)

    for i in range(len(img_path)):
        for j in range(len(img_path[i])):
            img = Image.open(app.root_path + '\\' + img_path[i][j])
            img.save(app.root_path + '\\' + 'static\\Data\\Zip\\' + user + '\\temp\\' + img_path[i][j].split(user)[1].split('@')[0] + '.' + img_path[i][j].split('.')[-1])

    root_dir = os.path.join(app.root_path, 'static\\Data\\Zip', user)
    shutil.make_archive('static\\Data\\Zip\\' + user + '\\' + user.split('@')[0], "zip", root_dir)
    shutil.rmtree(os.path.join(app.root_path, 'static\\Data\\Zip\\' + user, 'temp'))

    msg = MIMEMultipart()
    msg['Subject'] = 'Family Image Storage Server'
    msg['From'] = os.environ.get('SERVER_EMAIL_USERNAME')
    msg['To'] = user
    msg.attach(MIMEText('Dear Customer,\n\nData is in the Attachment.\n\nHave a Great Day!\nServer Admin', 'plain'))

    with open('static\\Data\\Zip\\' + user + '\\' + user.split('@')[0] + '.zip', 'rb') as f:
        attachment = f.read()

    part = MIMEBase('application', 'zip')
    part.set_payload(attachment)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename='Data.zip')
    msg.attach(part)
    msg = msg.as_string()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30) as smtp:
        smtp.login(os.environ.get('SERVER_EMAIL_USERNAME'), os.environ.get('SERVER_EMAIL_PASSWORD'))
        smtp.sendmail(os.environ.get('SERVER_EMAIL_USERNAME'), user, msg)
        smtp.close()


def get_file_size(images, user):
    path = glob.glob(os.path.join(app.root_path, 'static\\Data', user + '\\*'))
    size = 0

    for sub_path in path:
        size += os.path.getsize(sub_path)

    for image in images:
        size += sys.getsizeof(image)

    return size


def check_file(email):
    data = glob.glob(os.path.join(app.root_path, 'static/Data/' + email))

    if len(data) == 0:
        return True
    else:
        return False
