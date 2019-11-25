import os


if os.environ.get('DEBUG', 0):
    from .develop import *
else:
    from .production import *
