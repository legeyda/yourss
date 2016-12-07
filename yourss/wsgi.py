
from cherrypy import Application
from .server import envConfig
from .route import Root

# wsgi interface
application=Application(Root(envConfig.base_url()), script_name=None, config=None)
