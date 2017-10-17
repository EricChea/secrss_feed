"""Settings for Django channels"""

import os
import channels.asgi

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eldorado_webapp.settings")
channel_layer = channels.asgi.get_channel_layer()
