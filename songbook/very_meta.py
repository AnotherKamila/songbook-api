from .ref import Ref, refjoin

class NotFound(Exception): pass


class Viewable:
    def __init__(self, ref):
        self.ref = Ref(ref)
        assert self.TYPENAME == ref.typename, \
               'Cannot initialize "{}" as {}'.format(ref, self.__class__.__name__)

    def load(self, db, fromref=None):
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
        self.resolved_ref = None
        if len(self.ref) > self.REF_COMPONENTS['version']:
            self.resolved_ref = self.ref

    def resolve_ref(self, db):
        if not self.resolved_ref:
            resolved_version = db.get(self.ref)
            if not resolved_version: raise NotFound
            print('VersionedMixin: resolved version:', self.ref, '->', resolved_version)
            self.resolved_ref = refjoin(self.ref, resolved_version)

type_map = {}

def typename(typename):
    def typed(cls):
        cls.TYPENAME = typename
        type_map[typename] = cls
        return cls
    return typed
