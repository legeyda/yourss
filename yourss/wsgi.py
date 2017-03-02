
from cherrypy import Application
from .server import get_env_config
from .route import Root
from .valid import YourssServerParameters
from .stuff import without_keys

# wsgi interface
application=Application(Root(YourssServerParameters(**without_keys(get_env_config(), 'log_level')).valid_value()['base_url']), script_name=None, config=None)
