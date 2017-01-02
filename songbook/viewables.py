from .very_meta import Viewable, VersionedMixin, extra_ref_components, typename, type_map
from .ref import Ref, refjoin
from .db_conventions import contents_ref

INTERESTING_METADATA = ('title', 'artist')
def getmeta(db, ref):
    values = db.hmget(ref, INTERESTING_METADATA)
    return dict(zip(INTERESTING_METADATA, values))

class Item(VersionedMixin, Viewable):
    def load_meta(self, db, fromref=None):
        self.resolve_ref(db)
        self.data = getmeta(db, self.resolved_ref)
        return self

    def load(self, db, fromref=None):
        self.resolve_ref(db)
        self.data = db.hgetall(self.resolved_ref)
        return self

    def view(self, viewer):
        """May only be called after `load()`."""
        if self.ref == self.resolved_ref:
            return viewer.OK(self)
        else:
            return viewer.Alias(self.resolved_ref)

@typename('book')
@extra_ref_components('id', 'version')
class Book(Item):
    @classmethod
    def load_child(cls, db, ref):
        ref = Ref.from_str(ref)
        data = type_map[ref.typename](ref).load_meta(db).data
        data['ref'] = ref
        return data

    def load(self, db, fromref=None):
        # print(self.version, self_resolved)
        super(Book, self).load(db, fromref or self.ref)
        children = db.smembers(contents_ref(self.resolved_ref))
        self.data['contents'] = [self.load_child(db, c) for c in children]
        return self

@typename('song')
@extra_ref_components('id', 'version')
class Song(Item):
    pass  # yay abstractions :D
