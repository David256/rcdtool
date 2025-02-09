#!/usr/bin/env python

# MIT License
#
# Copyright (c) 2025 David256
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os
from typing import Union

import configparser
from telethon import TelegramClient
from telethon.functions import channels
from telethon.types import InputChannel, MessageMediaPaidMedia

from rcdtool.log import logger


class RCD:
    def __init__(self, config_filename: str):
        self.config_filename = config_filename
        self.config = self.get_config(self.config_filename)
        self.client = self.create_client()

    def get_config(self, config_filename: str):
        """Create a config object from config file.

        Args:
            config_filename (str): The config filename.

        Returns:
            ConfigParser: a new ConfigParser object.
        """
        if not os.path.exists(config_filename):
            raise FileNotFoundError(f'Not found: {config_filename}')
        config = configparser.ConfigParser()
        config.read(config_filename)
        return config

    def create_client(self):
        """Create a Telegram client object from given config.

        Args:
            config (configparser.ConfigParser): Parsed config object.

        Returns:
            TelegramClient: The Telegram client object.
        """
        client = TelegramClient(
            session=self.config['Access']['session'],
            api_id=self.config['Access']['id'],
            api_hash=self.config['Access']['hash'],
            timeout=int(self.config['Client']['timeout']),
            device_model=self.config['Client']['device_model'],
            lang_code=self.config['Client']['lang_code'],
        )
        client.start()
        return client

    async def download_media(self,
                      channel_id: Union[int, str],
                      message_id: int,
                      output_filename: str,
                      ):
        """Read a message in a channel and download the media to output.

        Args:
            client (TelegramClient): The Telegram client object.
            channel_id (int): The channel ID.
            message_id (int): The message ID.
            output_filename (str): The output filename.
        """
        entity = await self.client.get_entity(channel_id)

        input_channel = InputChannel(entity.id, entity.access_hash)


        messages_request = channels.GetMessagesRequest(input_channel, [message_id])
        channel_messages: messages.Messages = await self.client(messages_request)
        messages = channel_messages.messages

        message = messages[0]

        logger.info('downloading...')

        with open(output_filename, 'wb+') as file:
            if isinstance(message.media, MessageMediaPaidMedia):
                logger.debug('paid message found')
                for message_extended_media in message.media.extended_media:
                    await self.client.download_file(message_extended_media.media, file)
            else:
                await self.client.download_file(message.media, file)
            logger.info('downloaded to %s', output_filename)
