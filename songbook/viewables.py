from .very_meta import Viewable, VersionedMixin, NotFound, extra_ref_components, typename
from .ref import refjoin
from .db_conventions import contents_ref

class Item(Viewable):
    def load(self, db, fromref=None):
        self.data = db.hgetall(fromref or self.ref)
        return self

@typename('book')
@extra_ref_components('id', 'version')
class Book(VersionedMixin, Item):
    def load(self, db, fromref=None):
        # print(self.version, self_resolved)
        super(Book, self).load(db, fromref or self.ref)
        self.data['contents'] = db.smembers(contents_ref(self.resolved_ref))
        return self

@typename('song')
@extra_ref_components('id', 'version')
class Song(VersionedMixin, Item):
    pass  # yay abstractions :D
