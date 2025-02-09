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

import sys
from dataclasses import dataclass
from typing import Optional, Union, cast
import argparse
from random import randrange

from rcdtool.rcdtool import get_config, create_client, process


@dataclass
class Arguments:
    """Arguments."""
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


def main():
    """
    The main method.
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
