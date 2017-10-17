"""
WSGI config for eldorado_webapp project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eldorado_webapp.settings")

application = get_wsgi_application()
