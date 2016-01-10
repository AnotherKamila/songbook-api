KEYSEP = '/'

class Ref(tuple):
    """Uniquely identifies an object stored in the database.

    The first component of the ref identifies the object's type, so
    if r1[0] == r2[0], then those two objects are of the same type.
    """
    TYPE = 0  # index of type in the ref field

    def __init__(self, args):
        assert isinstance(args, (tuple, list)) and len(args) > 0, 'you are ugly'
        args = [ str(x) for x in args ]
        tuple.__init__(args)

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
        assert self.typename == ref[self.REF_TYPE], \
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
        self.live_version = self.version

    def resolve_version(self, db, ref):
        if self.live_version is None:
            live_ref = db.get(self.ref)
            print('VersionedMixin: resolved version:', self.ref, '->', live_ref)
            if live_ref is None: raise NotFound
            live_ref = Ref.from_str(live_ref)
            self.live_version = live_ref[self.REF_VERSION]

    def live_ref(self):
        return Ref((self.typename, self.id, self.live_version))

    @classmethod
    def load_versioned_with_op(cls, db, ref, operation):
        x = cls(ref)
        x.resolve_version(db, ref)
        if not x.live_version: raise NotFound
        print('loading from DB:', x.live_ref())
        x.contents = operation(x.live_ref())
        if not x.contents: raise NotFound
        return x

    def view(self, viewer):
        """May only be called after `load()`."""
        if self.version == self.live_version:
            return viewer.OK(self)
        else:
            return viewer.Alias(self.live_ref())

type_map = {}

def model_typename(typename):
    def _model_typename(cls):
        cls.typename = typename
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
