from itertools import chain
from .utils import to_utf8

KEYSEP = '/'

def is_reflike(x):
    return isinstance(x, (tuple, list, Ref))

class Ref(tuple):
    """Uniquely identifies an object stored in the database.

    The first component of the ref identifies the object's type, so
    if r1[0] == r2[0], then those two objects are of the same type.
    """
    @property
    def typename(self):
        return self[0]

    def __new__(cls, arg):
        if not isinstance(arg, (tuple, list)) and len(arg) >= 1: raise ValueError('you are ugly')
        arg = [to_utf8(x) for x in arg]
        return tuple.__new__(cls, arg)

    @classmethod
    def from_str(cls, s):
        args = to_utf8(s).split(KEYSEP)
        return cls(args)

    def __repr__(self):
        return KEYSEP.join(self)

def refjoin(*args):
    args = [a if is_reflike(a) else Ref.from_str(a) for a in args]
    return Ref(list(chain(*args)))
