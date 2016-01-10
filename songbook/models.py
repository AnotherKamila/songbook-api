KEYSEP = '/'

class Ref(tuple):
    """Uniquely identifies an object stored in the database.

    The first component of the ref identifies the object's type, so
    if r1[0] == r2[0], then those two objects are of the same type.
    """
    TYPE = 0  # index of type in the ref field

    def __new__(cls, arg):
        assert isinstance(arg, (tuple, list)) and len(arg) > 0, 'you are ugly'
        arg = [ x.decode(encoding='UTF-8') if isinstance(x, (bytes,bytearray)) else str(x) for x in arg ]
        return tuple.__new__(cls, arg)

    @classmethod
    def from_str(cls, s):
        if isinstance(s, (bytes, bytearray)): s = s.decode(encoding='UTF-8')
        args = s.split(KEYSEP)
        return cls(args)

    def __repr__(self):
        return KEYSEP.join(self)

class NotFound(Exception): pass

class Model:
    REF_TYPE = Ref.TYPE
    REF_ID   = REF_TYPE + 1

    def __init__(self, ref):
        ref = Ref(ref)
        assert self.TYPENAME == ref[self.REF_TYPE], \
            'Cannot load "{}" as {}'.format(ref, self.__class__.__name__)
        self.ref = ref
        self.id = ref[self.REF_ID]

    @classmethod
    def load(cls, db, ref):
        raise NotImplementedError('Cannot load an abstract Model.')

    def view(self, viewer):
        raise NotImplementedError('Cannot view an abstract Model.')

class VersionedMixin:
    REF_VERSION = Model.REF_ID + 1

    def __init__(self, ref):
        super(VersionedMixin, self).__init__(ref)
        self.version = None
        if len(ref) > self.REF_VERSION:
            self.version = ref[self.REF_VERSION]
        self.resolved_version = self.version
        if len(ref) > self.REF_VERSION + 1: raise NotFound

    def resolve_version(self, db, ref):
        if self.resolved_version is None:
            self.resolved_version = db.get(self.ref)
            print('VersionedMixin: resolving version:', self.ref, '->', self.resolved_version)

    def resolved_ref(self):
        return Ref((self.TYPENAME, self.id, self.resolved_version))

    @classmethod
    def load_versioned_with_op(cls, db, ref, load_op):
        x = cls(ref)
        x.resolve_version(db, ref)
        if not x.resolved_version: raise NotFound
        print('loading from DB:', x.resolved_ref())
        x.contents = load_op(x.resolved_ref())
        if not x.contents: raise NotFound
        return x

    def view(self, viewer):
        """May only be called after `load()`."""
        if self.version == self.resolved_version:
            return viewer.OK(self)
        else:
            return viewer.Alias(self.resolved_ref())

type_map = {}

def model_typename(typename):
    def _model_typename(cls):
        cls.TYPENAME = typename
        type_map[typename] = cls
    return _model_typename

@model_typename('book')
class Book(VersionedMixin, Model):
    @classmethod
    def load(cls, db, ref):
        return cls.load_versioned_with_op(db, ref, db.smembers)

@model_typename('song')
class Song(VersionedMixin, Model):
    @classmethod
    def load(cls, db, ref):
        return cls.load_versioned_with_op(db, ref, db.hgetall)
