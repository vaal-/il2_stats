from django.utils.version import get_version

# VERSION = (1, 9, 0, 'alpha', 0)

# __version__ = get_version(VERSION)

# https://www.python.org/dev/peps/pep-0440/

VERSION = (1, 2, 61)
__version__ = '.'.join(map(str, VERSION))
