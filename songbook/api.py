import cherrypy
from .models import KEYSEP

# TODO this is ugly and coupled and just horrible and would break if anyone ever decided to refactor this
def key2url(key): return '/'+key.replace(KEYSEP, '/')
def key2type(key): return key.split(KEYSEP)[0]

@cherrypy.tools.json_in()
@cherrypy.tools.json_out()
class Resource(object):
    exposed = True

    def __init__(self, **kwargs):
        self.args = kwargs

    @property
    def modelCls(self):
        try:
            return self._modelCls
        except AttributeError:
            self._modelCls = getattr(cherrypy.request.app.root.args['models'], self.__class__.__name__)
            return self._modelCls

    def url(self, id):
        return '/'+self.modelCls(id).ref(sep='/')

    @cherrypy.popargs('id')
    @cherrypy.popargs('version')
    def GET(self, id=None, version=None):
        if not id:
            try:
                self.index()
            except AttributeError:
                raise cherrypy.NotFound()

        model = self.modelCls(id, version)
        model.load()
        return model.contents

class Book(Resource):
    def GET(self, id=None, version=None):
        return [ { 'type': key2type(x), 'url': key2url(x) } for x in super().GET(id, version) ]

class Song(Resource): pass

class Root(Resource):
    book = Book()    
    song = Song()

cpconfig = {
    '/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    },
}
