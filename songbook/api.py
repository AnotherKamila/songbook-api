from http import HTTPStatus as S

import cherrypy

from . import items
from . import very_meta
from . import auth
from .ref import refjoin
from .utils import ref2url, json_friendly, http_viewer, to_utf8

Err = cherrypy.HTTPError

@cherrypy.tools.json_in()
@cherrypy.tools.json_out()
class Root(object):
    exposed = True

    def __init__(self, db_conn):
        self.db = db_conn

    def _find_object(self, args, on_error_return=None, on_error_raise=None):
        if len(args) < 1:
            if on_error_return: return on_error_return
            if on_error_raise: raise on_error_raise
        ref = very_meta.Ref(args)
        try:
            return ref, very_meta.type_map[ref.typename](ref)
        except KeyError as e:
            http_viewer.NotFound(e)


    def GET(self, *args):
        ref, item = self._find_object(args, on_error_return={'api_docs': 'TODO'})
        try:
            return item.load(self.db).view(http_viewer)
        except very_meta.NotFound as e:
            http_viewer.NotFound(e)

    def POST(self, *args):
        ref, item = self._find_object(args, on_error_raise=Err(S.METHOD_NOT_ALLOWED.value))

        user = auth.user(cherrypy.request.json.get('user'), self.db)
        if not user: raise Err(401)
        self.db.setnx(refjoin(item.unversioned_ref, 'owner'), user)
        item.set(cherrypy.request.json.get('data',{})).save(self.db)
        url = cherrypy.request.base+ref2url(item.ref)
        cherrypy.response.status = S.CREATED.value
        cherrypy.response.headers['Location'] = url
        return {'url': url, 'version': item.version}

    def PUT(self, *args):
        ref, item = self._find_object(args, on_error_raise=Err(S.METHOD_NOT_ALLOWED.value))
        version = cherrypy.request.json.get('version')
        if not version: raise Err(S.BAD_REQUEST.value)
        user = auth.user(cherrypy.request.json.get('user'), self.db)
        if not user: raise Err(401)
        owner = to_utf8(self.db.get(refjoin(item.unversioned_ref, 'owner')))
        if user != owner: raise Err(403)
        item.set_default_version(self.db, version)


cpconfig = {
    '/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    },
}
