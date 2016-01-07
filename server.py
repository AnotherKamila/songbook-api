import cherrypy
import redis

import os

class App(object):
    def __init__(self, db_conn):
        self.db_conn=db_conn

    @cherrypy.expose
    def index(self):
        return 'foo: '+str(db.smembers('foo'))

db = redis.from_url(os.environ.get('REDISCLOUD_URL'))

cherrypy.config.update({
    'server.socket_host': '0.0.0.0',
    'server.socket_port': int(os.environ.get('PORT', '5000')),
    'tools.proxy.on': True,
})
cherrypy.quickstart(App(db_conn=db))
