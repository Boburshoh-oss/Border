from datetime import datetime, timedelta

import json

import requests

from django.conf import settings

def sms_login():
    r = requests.post(settings.SMS_BASE_URL + '/api/auth/login/',
                      {'email': settings.SMS_EMAIL, 'password': settings.SMS_SECRET_KEY}).json()
    settings.SMS_TOKEN = r['data']['token']


def sms_refresh():
    r = requests.patch(settings.SMS_BASE_URL + '/api/auth/refresh',
                       headers={'Authorization': f'Bearer {settings.SMS_TOKEN}'}).json()
    settings.SMS_TOKEN = r['data']['token']


def sendSmsOneContact(phone_number, text):
    sms_login()
    phone_number = str(phone_number)
    phone_number.replace("+", "")
    try:
        if phone_number.startswith("998"):
            return requests.post(
                settings.SMS_BASE_URL + '/api/message/sms/send',
                {'mobile_phone': phone_number, 'message': text},
                headers={'Authorization': f'Bearer {settings.SMS_TOKEN}'},
            ).json()
    except Exception as e:
        print(e)
        return None