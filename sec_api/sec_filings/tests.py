"""Tests for sec_filings application"""

import json

from channels import Channel
from channels.test import ChannelTestCase

from sec_filings import consumers

class CopyTestCase(ChannelTestCase):


    def test_end_to_end(self):

        send_channel = 'test_send_channel'
        reply_channel = 'test_reply_channel'

        # Inject a message onto the channel to use in a consumer
        # The 'reply_channel' is a required parameter since the ws_message
        # consumer is decorated with @channel_session.
        Channel(send_channel).send({
            'text': 'Does data get into send_channel?',
            'reply_channel': reply_channel
        })

        # Run the consumer with the new Message object.
        consumers.ws_message(self.get_next_message(send_channel, require=True))

        # Verify there's a result was posted to the reply channel by ws_message.
        result = self.get_next_message(reply_channel, require=True)

        self.assertEqual(result['text'], json.dumps({'companies': []}))
