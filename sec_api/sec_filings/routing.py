"""Routing for socket listeners and publishers"""

from channels.routing import route
from sec_filings import consumers

channel_routing = [
    route('websocket.connect', consumers.ws_connect),
    route('websocket.new_message', consumers.ws_message, path=r'^/feed/$'),
]
