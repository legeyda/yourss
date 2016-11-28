from distutils.core import setup
from pip.req import parse_requirements
from yourss import VERSION
from os.path import join, dirname

setup(
    name = 'yourss',
    version = VERSION,
    description = 'youtube video to rss',
    keywords = 'rss youtube youtube-dl ',
    author = 'legeyda',
    author_email = '',
    maintainer = '',
    maintainer_email = '',
    url = 'http://github.com/legeyda/yourss',
    dependency_links = [str(r.req) for r in parse_requirements(join(dirname(__file__), 'requirements.txt'))],
    packages = ['yourss'],
    include_package_data = True,
)