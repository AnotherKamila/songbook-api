from .ref import Ref, refjoin

class NotFound(Exception): pass


class SavedObject:
    def __init__(self, ref):
        self.ref = Ref(ref)
        assert self.TYPENAME == ref.typename, \
               'Cannot initialize "{}" as {}'.format(ref, self.__class__.__name__)

    def load(self, db, fromref=None):
        raise NotImplementedError('Cannot load an abstract SavedObject.')

    def set(self, data):
        raise NotImplementedError('Cannot set an abstract SavedObject.')

    def save(self, db):
        raise NotImplementedError('Cannot save an abstract SavedObject.')

    def view(self, viewer):
        raise NotImplementedError('Cannot view an abstract SavedObject.')

def extra_ref_components(*args):
    def add_ref_components(cls):
        cls.REF_COMPONENTS = {args[i]: i+1 for i in range(len(args))}  # 0 is type
        return cls
    return add_ref_components


class VersionedMixin:
    def __init__(self, ref):
        super(VersionedMixin, self).__init__(ref)
        self.resolved_ref = None
        if self.version:
            self.resolved_ref = self.ref

    def resolve_ref(self, db):
        if not self.resolved_ref:
            resolved_version = db.get(self.ref)
            if not resolved_version: raise NotFound("Could not resolve `{}'".format(self.ref))
            print('VersionedMixin: resolved version:', self.ref, '->', resolved_version)
            self.resolved_ref = refjoin(self.ref, resolved_version)

    @property
    def unversioned_ref(self):
        return Ref(self.ref[:self.REF_COMPONENTS['version']])

    @property
    def version(self):
        if len(self.ref) > self.REF_COMPONENTS['version']:
            return self.ref[self.REF_COMPONENTS['version']]

    def new_version(self, db):
        self.ref = refjoin(self.unversioned_ref, db.incr(refjoin(self.unversioned_ref, 'version_counter')))

    def set_default_version(self, db, version):
        db.set(self.unversioned_ref, version)


type_map = {}

def typename(type_name):
    def typed(cls):
        cls.TYPENAME = type_name
        type_map[type_name] = cls
        return cls
    return typed
