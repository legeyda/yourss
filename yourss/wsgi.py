
from cherrypy import Application
from . import envConfig
from .route import Root

# wsgi interface
application=Application(Root(envConfig.base_url()), script_name=None, config=None)
