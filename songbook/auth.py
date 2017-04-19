from .ref import refjoin
from .utils import to_utf8

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
}
def user(d, db):
    """Authenticates a user, or returns None if auth failed.

    d is a "user descriptor" dict: contains a 'type' field that is one of
    the above, and some other stuff (depends on type).
    """
    if d and 'type' in d and d['type'] in types:
        return types[d['type']](d, db)
