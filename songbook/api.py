from . import viewables
from . import very_meta

import cherrypy

def ref2url(ref): return '/' + '/'.join(ref)

def json_friendly(obj):
    """Converts Python objects into similar objects which can be JSONified."""
    if isinstance(obj, very_meta.Ref):
        return repr(obj)
    if isinstance(obj, (set, list, tuple)):
        return [json_friendly(x) for x in obj]
    if isinstance(obj, dict):
        return {json_friendly(k): json_friendly(v) for k, v in obj.items()}
    if isinstance(obj, (bytes, bytearray)):
        return obj.decode(encoding='utf-8')
    else:
        return obj

class http_viewer:
    """Translates viewables into HTTP responses."""
    def OK(viewable):
        return json_friendly(viewable.data)

    def Alias(to):
        raise cherrypy.HTTPRedirect(ref2url(to), 302)

    def NotFound(err):
        if isinstance(err, Exception):
            raise cherrypy.NotFound from err
        else:
            raise cherrypy.NotFound(err)

@cherrypy.tools.json_in()
@cherrypy.tools.json_out()
class Root(object):
    exposed = True

    def __init__(self, db_conn):
        self.db = db_conn

    def GET(self, *args):
        if len(args) < 1: return {'api_docs': 'TODO'}
        ref = very_meta.Ref(args)

        try:
            return very_meta.type_map[ref.typename].load(self.db, ref).view(http_viewer)
        except (KeyError, very_meta.NotFound) as e:
            http_viewer.NotFound(e)

cpconfig = {
    '/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    },
}
