import cherrypy
import redis

import os

class App(object):
    def __init__(self, db_url):
        self.db_conn = redis.from_url(db_url)

    @cherrypy.expose
    def index(self):
        return 'foo: '+str(self.db_conn.smembers('foo'))

app = App(
    db_url=os.environ.get('REDISCLOUD_URL'),
)

cherrypy.config.update({
    'server.socket_host': '0.0.0.0',
    'server.socket_port': int(os.environ.get('PORT', '5000')),
    'tools.proxy.on': True,
})
cherrypy.quickstart(app)
