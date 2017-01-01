from .ref import Ref, refjoin

class NotFound(Exception): pass


class Viewable:
    def __init__(self, ref):
        self.ref = Ref(ref)
        assert(self.TYPENAME == ref.typename,
               'Cannot load "{}" as {}'.format(ref, self.__class__.__name__))

    @classmethod
    def load(cls, db, ref):
        raise NotImplementedError('Cannot load an abstract Viewable.')

    def view(self, viewer):
        raise NotImplementedError('Cannot view an abstract Viewable.')

def extra_ref_components(*args):
    def add_ref_components(cls):
        cls.REF_COMPONENTS = {args[i]: i+1 for i in range(len(args))}  # 0 is type
        return cls
    return add_ref_components


class VersionedMixin:
    def __init__(self, ref):
        super(VersionedMixin, self).__init__(ref)
        self.version = None
        if len(self.ref) > self.REF_COMPONENTS['version']:
            self.version = self.ref[self.REF_INDEX_VERSION]
        self.resolved_version = self.version

    def resolve_version(self, db, ref):
        if self.resolved_version is None:
            self.resolved_version = db.get(self.ref)
            print('VersionedMixin: resolving version:', self.ref, '->', self.resolved_version)

    @property
    def resolved_ref(self):
        return refjoin(self.ref, [self.resolved_version])

    @classmethod
    def load_versioned_with_op(cls, db, ref, load_op):
        x = cls(ref)
        x.resolve_version(db, ref)
        if not x.resolved_version: raise NotFound
        print('loading from DB:', x.resolved_ref)
        x.data = load_op(x.resolved_ref)
        if not x.data: raise NotFound
        return x

    def view(self, viewer):
        """May only be called after `load()`."""
        if self.version == self.resolved_version:
            return viewer.OK(self)
        else:
            return viewer.Alias(self.resolved_ref)


type_map = {}

def typename(typename):
    def typed(cls):
        cls.TYPENAME = typename
        type_map[typename] = cls
        return cls
    return typed
