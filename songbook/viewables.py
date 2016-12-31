from .very_meta import Viewable, VersionedMixin, NotFound, extra_ref_components, typename

@typename('book')
@extra_ref_components('id', 'version')
class Book(VersionedMixin, Viewable):
    @classmethod
    def load(cls, db, ref):
        return cls.load_versioned_with_op(db, ref, db.smembers)

@typename('song')
@extra_ref_components('id', 'version')
class Song(VersionedMixin, Viewable):
    @classmethod
    def load(cls, db, ref):
        return cls.load_versioned_with_op(db, ref, db.hgetall)

@typename('public_songbooks')
class PublicSongbooks(Viewable):
    @classmethod
    def load(cls, db, ref):
        print('public_songbooks got ref: ', ref)
        x = cls(ref)
        x.data = db.smembers(ref)
        return x

    def view(self, viewer):
        return viewer.OK(self)

