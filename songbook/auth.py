import os
from datetime import datetime, timezone

import iso8601
import requests

from .ref import refjoin
from .utils import to_utf8

RECAPTCHA_DIFF = 60  # seconds

def recaptcha(token):
    r = requests.post('https://www.google.com/recaptcha/api/siteverify',
                  data={
                      'secret': os.environ['RECAPTCHA_SECRET'],
                      'response': token,
                  })
    print(r.json())
    if r.json()['success']:
        ts = iso8601.parse_date(r.json()['challenge_ts'])
        return abs((datetime.now(timezone.utc) - ts).total_seconds()) < RECAPTCHA_DIFF

def with_recaptcha(fn):
    def decorated(d, db):
        if 'recaptcha' in d and recaptcha(d['recaptcha']):
            return fn(d, db)

def passcode(d, db):
    # TODO hash passcodes
    code = d.get('passcode')
    print('code for', d['id'], db.get(refjoin('user', d['id'], 'passcode')))
    if code == to_utf8(db.get(refjoin('user', d['id'], 'passcode'))):
        return d['id']

def google(d, db):
    # TODO verify tokens
    raise NotImplemented


types = {
    'passcode': passcode,
    'google': google,
    'script': ...
}
def user(d, db):
    """Authenticates a user, or returns None if auth failed.

    d is a "user descriptor" dict: contains a 'type' field that is one of
    the above, and some other stuff (depends on type).
    """
    if d and 'type' in d and d['type'] in types:
        return types[d['type']](d, db)
