"""Workloads to consume by workers spun up in Django Channels"""

import json

from django.http.request import HttpRequest
from channels import Group

from sec_filings import views
from sec_filings import constants


def broadcast_message(response, group):
    """Broadcasts the contents of a response object to the specified group."""
    message_content = dict(content=json.loads(response.content), path=r'/feed/')
    Group(constants.SEC_GROUP).send(dict(text=json.dumps(message_content)))


def ws_connect(message):
    """Connect a client to the open websocket and send data on connect."""
    Group(constants.SEC_GROUP).add(message.reply_channel)
    ws_message(message)


def ws_message(message):
    """Publishes data into the websocket for consumption from the frontend.

    When new data is available in the SEC rss feed this function is triggered.
    All clients that have subscribed to the sec group will receive the new data.
    """
    response = views.get_feed(HttpRequest())
    broadcast_message(response, constants.SEC_GROUP)


def ws_disconnect(message):
    """Disconnect a listener from the group."""
    Group(constants.SEC_GROUP).discard(message.reply_channel)
