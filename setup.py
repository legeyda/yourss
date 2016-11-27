from distutils.core import setup

setup(
    name = 'yourss',
    version = '0.1.0',
    description = 'youtube2rss',
    keywords = 'youtube youtube-dl ',
    author = 'legeyda',
    author_email = '',
    maintainer = '',
    maintainer_email = '',
    url = 'http://bitbucket.org/legeyda/yourss',
    dependency_links = ['CherryPy', ],
    packages = ['yourss'],
    include_package_data = True,
    entry_points={
        'console_scripts': [
            'rss2sms=rss2sms:main',
        ],
    },
)