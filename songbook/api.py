from . import models

import cherrypy

def ref2url(ref): return '/' + '/'.join(ref)

def json_friendly(obj):
    """Converts Python objects into similar objects which can be JSONified."""
    if isinstance(obj, models.Ref):
        return repr(obj)
    if isinstance(obj, (set, list, tuple)):
        return [ json_friendly(x) for x in obj ]
    if isinstance(obj, dict):
        return { json_friendly(k): json_friendly(v) for k, v in obj.items() }
    if isinstance(obj, (bytes, bytearray)):
        return obj.decode(encoding='UTF-8')
    else:
        return obj

class http_viewer:
    """Translates models into HTTP responses."""
    def OK(data):
        return json_friendly(data.contents)

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
        if len(args) < 2: return { 'api_docs': 'TODO' }
        ref = models.Ref(args)

        typename = ref[models.Ref.TYPE]
        try:
            return models.type_map[typename].load(self.db, ref).view(http_viewer)
        except (KeyError, models.NotFound) as e:
            http_viewer.NotFound(e)

cpconfig = {
    '/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    },
}
