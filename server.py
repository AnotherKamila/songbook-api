from songbook import api, models

import cherrypy
import redis
import os
import sys

db_url = os.environ.get('REDISCLOUD_URL')
if not db_url: sys.exit('REDISCLOUD_URL not set, exiting.')
ms = models.with_db_conn(redis.from_url(db_url))

cherrypy.config.update({
    'server.socket_host': '0.0.0.0',
    'server.socket_port': int(os.environ.get('PORT', '5000')),
    'tools.proxy.on': True,
})
cherrypy.quickstart(api.Root(models=ms), '/', api.cpconfig)
