from http import HTTPStatus as S

import cherrypy

from . import very_meta

def ref2url(ref): return '/' + '/'.join(ref)

def to_utf8(x):
    if x is None: return None
    if isinstance(x, (bytes, bytearray)):
        return x.decode(encoding='utf-8')
    return str(x)

def json_friendly(obj):
    """Converts Python objects into similar objects which can be JSONified."""
    if isinstance(obj, very_meta.Ref):
        return ref2url(obj)
    if isinstance(obj, (set, list, tuple)):
        return [json_friendly(x) for x in obj]
    if isinstance(obj, dict):
        return {json_friendly(k): json_friendly(v) for k, v in obj.items()}
    if isinstance(obj, (bytes, bytearray)):
        return to_utf8(obj)
    else:
        return obj

class http_viewer:
    """Translates items into HTTP responses."""
    def OK(viewable):
        return json_friendly(viewable.data)

    def Alias(to):
        raise cherrypy.HTTPRedirect(ref2url(to), S.FOUND)

    def NotFound(err):
        if isinstance(err, Exception):
            raise cherrypy.NotFound from err
        else:
            raise cherrypy.NotFound(err)

