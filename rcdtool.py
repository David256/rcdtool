#!/usr/bin/env python

# MIT License
#
# Copyright (c) 2023 David256
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
from dataclasses import dataclass
from typing import Optional, Union, cast
import argparse
import sys
import readline
from random import randrange

import configparser
from telethon import TelegramClient
from telethon.functions import channels
from telethon.types import InputChannel

@dataclass
class Arguments:
    config_filename: str
    channel_id: Optional[str]
    message_id: Optional[str]
    output_filename: Optional[str]
    link: Optional[str]


def get_args():
    """Parser the CLI arguments and return a Namespace object.

    Returns:
        Namespace: Parsed CLI arguments.
    """
    parser = argparse.ArgumentParser(
        prog='rcdtool',
        description=(
            'Script that uses the Telegram API to download any media by '
            'private message link of channel where you are member'
        )
    )

    parser.add_argument('--link',
                        nargs='?',
                        dest='link',
                        const="",
                        default=None,
                        help='Take IDs from a message link')
    parser.add_argument('-c',
                        '--config',
                        nargs='?',
                        dest='config_filename',
                        default='config.ini',
                        help='The config filename')
    parser.add_argument('-C',
                        '--channel-id',
                        nargs='?',
                        dest='channel_id',
                        help='The channel ID or username')
    parser.add_argument('-M',
                        '--message-id',
                        nargs='?',
                        dest='message_id',
                        help='The message ID')
    parser.add_argument('-O',
                        '--output',
                        nargs='?',
                        dest='output_filename',
                        help='The output filename')
    return cast(Arguments, parser.parse_args())


def get_config(config_filename: str):
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


def create_client(config: configparser.ConfigParser):
    """Create a Telegram client object from given config.

    Args:
        config (configparser.ConfigParser): Parsed config object.

    Returns:
        TelegramClient: The Telegram client object.
    """
    client = TelegramClient(
        session=config['Access']['session'],
        api_id=config['Access']['id'],
        api_hash=config['Access']['hash'],
        timeout=int(config['Client']['timeout']),
        device_model=config['Client']['device_model'],
        lang_code=config['Client']['lang_code'],
    )
    client.start()
    return client

async def process(client: TelegramClient,
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
    entity = await client.get_entity(channel_id)
    # print(entity)

    input_channel = InputChannel(entity.id, entity.access_hash)


    messages_request = channels.GetMessagesRequest(input_channel, [message_id])
    channel_messages: messages.ChannelMessages = await client(messages_request)
    messages = channel_messages.messages

    message = messages[0]
    # print(message)

    print('downloading...')

    with open(output_filename, 'wb+') as file:
        await client.download_file(message.media, file)
        print(f'downloaded to {output_filename}')


def main():
    """
    curl affinity favour settlement weak stride industry censorship democratic
    forbid role listen sense defendant patience withdraw challenge article AIDS
    herb riot contrary overview friendly worker conceive stream favorable
    second squash experiment session symbol contemporary counter temptation beef
    """
    args = get_args()
    config = get_config(args.config_filename)
    
    if args.link is None:
        # Take the channel ID or ask for this
        if args.channel_id is None:
            channel_id = input('Channel ID: ')
        else:
            channel_id = args.channel_id
        
        # Take the message ID or ask for this
        if args.message_id is None:
            message_id = input('Message ID: ')
        else:
            message_id = args.message_id
    else:
        message_link = args.link
        if message_link == "":
            message_link = input('Message link: ')
        channel_id, message_id = message_link.split('/')[-2:]

    # Check if the channel_id is valid
    updated_channel_id: Union[int, str] = channel_id
    try:
        updated_channel_id = int(channel_id)
        if updated_channel_id > 0:
            updated_channel_id = int(f'-100{updated_channel_id}')
    except ValueError as err:
        print('channel id from string because', err)

    # Get the output filename
    if args.output_filename is None:
        output_filename = f'file-{randrange(00000, 99999)}'
    else:
        output_filename = args.output_filename

    client = create_client(config)

    coro = process(client=client,
                   channel_id=updated_channel_id,
                   message_id=int(message_id),
                   output_filename=output_filename,
                   )
    client.loop.run_until_complete(coro)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e, file=sys.stderr, flush=True)
        sys.exit(-1)
