# site
AUTHOR = 'theeluwin'
SITENAME = "theeluwin archive"
SITEURL = 'https://theeluwin.github.io'
SITEDESCRIPTION = "theeluwin archive"
GOOGLE_ANALYTICS_ID = 'UA-36051760-9'

# time
TIMEZONE = 'Asia/Seoul'
DEFAULT_LANG = 'ko'
DEFAULT_DATE_FORMAT = '%Y. %m. %d.'

# urls
RELATIVE_URLS = True

# contents
PATH = 'content/'
THEME = 'theme/'

# categories
USE_FOLDER_AS_CATEGORY = False
DEFAULT_CATEGORY = 'Essay'
CATEGORY_URL = 'category/{slug}/'
CATEGORY_SAVE_AS = 'category/{slug}/index.html'
CATEGORIES_SAVE_AS = ''

# articles
ARTICLE_PATHS = [
    'articles',
]
ARTICLE_URL = 'article/{slug}/'
ARTICLE_SAVE_AS = 'article/{slug}/index.html'
PATH_METADATA = r'articles/(?P<category>[^/]+)/(?P<year>\d{4})/(?P<slug>[^/]+)/.*'
SUMMARY_MAX_LENGTH = 70

# tags
TAG_URL = 'tag/{slug}/'
TAG_SAVE_AS = 'tag/{slug}/index.html'
TAGS_SAVE_AS = ''

# others
AUTHOR_SAVE_AS = ''
AUTHORS_SAVE_AS = ''
ARCHIVES_SAVE_AS = ''

# statics
STATIC_PATHS = [
    'articles',
    'images',
    'pdfs',
    'extra',
]
STATIC_EXCLUDE_SOURCES = True
EXTRA_PATH_METADATA = {
    'extra/favicon.ico': {'path': 'favicon.ico'},
    'extra/robots.txt': {'path': 'robots.txt'},
}

# plugins
PLUGIN_PATHS = ['plugins/']
PLUGINS = [
    'pelican.plugins.sitemap',
]
MARKDOWN = {
    'extensions': [
        'fenced_code',
        'codehilite',
        'attr_list',
        'tables',
    ],
    'extension_configs': {
        'codehilite': {
            'css_class': 'highlight',
            'guess_lang': False,
            'linenums': False,
        },
    },
}

# sitemap
SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.5,
        'indexes': 0.5,
    },
    'changefreqs': {
        'articles': 'weekly',
        'indexes': 'weekly',
    },
    'exclude': [
        'author',
        'extra',
    ],
}
