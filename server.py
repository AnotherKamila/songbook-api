from songbook import api

import cherrypy
import redis
import os
import sys

db_url = os.environ.get('REDISCLOUD_URL')
if not db_url: sys.exit('REDISCLOUD_URL not set, exiting.')
db_conn = redis.from_url(db_url)

def kill_default_logging():
    cherrypy.log.error_file = cherrypy.log.access_file = ''
    cherrypy.log.screen = False

cherrypy.config.update({
    'server.socket_host': '0.0.0.0',
    'server.socket_port': int(os.environ.get('PORT', '5000')),
})
cherrypy.quickstart(api.Root(db_conn=db_conn), '/', api.cpconfig)
