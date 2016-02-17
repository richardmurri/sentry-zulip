try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('sentry-zulip').version
except Exception, e:
    VERSION = 'unknown'
