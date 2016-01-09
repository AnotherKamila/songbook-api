import redis

KEYSEP = ':'

def b2s(b): return b.decode(encoding='UTF-8')

# TODO this is also horrible -- db should be passed to models in a different way
def with_db_conn(db):
    class ModelMixin(object):
        def __init__(self, id, version=None):
            self.id = id
            self.version = version
            if version: self.real_version = version
            else:  # find the newest version
                d = db.get(self.ref())
                f = b2s(d).split(KEYSEP)
                assert f[0] == self.typename and f[1] == self.id, 'Database integrity broken!!!!1!'
                self.real_version = f[2]
            self.key = self.ref(version=True)
            print('requested:', id, version, '->', self.key)

        def ref(self, sep=KEYSEP, version=False):
            fs = [self.typename, self.id]
            if version: fs.append(self.real_version)
            return sep.join(fs)

        def __repr__(self):
            return self.ref()

    class WithDBConn(object):
        class Book(ModelMixin):
            typename = 'book'
            
            def load(self):
                self.contents = { b2s(x) for x in db.smembers(self.key) }

        class Song(ModelMixin):
            typename = 'song'
            ...
            
            def load(self):
                self.contents = { b2s(k): b2s(v) for k, v in db.hgetall(self.key).items() }

    return WithDBConn

