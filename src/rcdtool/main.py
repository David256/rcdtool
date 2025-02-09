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

# pylint: disable=unused-import
import readline
import asyncio
from dataclasses import dataclass
from typing import Optional, Coroutine, cast
import argparse

from rcdtool.rcdtool import RCD

import rcdtool.utils as utils
from rcdtool.log import logger


@dataclass
class Arguments:
    """Arguments."""
    config_filename: str
    channel_id: Optional[str]
    message_id: Optional[str]
    output_filename: Optional[str]
    link: Optional[str]
    infer_extension: Optional[bool]
    dry_mode: Optional[bool]


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
    parser.add_argument('--infer-extension',
                        dest='infer_extension',
                        action='store_true',
                        default=False,
                        help='Infer extension and rename the output file')
    parser.add_argument('--dry-mode',
                        dest='dry_mode',
                        action='store_true',
                        default=False,
                        help='Active the dry mode')
    return cast(Arguments, parser.parse_args())


def main():
    """
    The main method.
    """
    args = get_args()

    rcd_tool = RCD(args.config_filename, dry_mode=args.dry_mode)

    raw_targets: list[tuple[str, str]] = []

    if args.link is None:
        channel_id = args.channel_id or input('Channel ID: ')

        message_id_input = args.message_id or input('Message ID: ')
        range_message_id = utils.parse_ranges(message_id_input)

        for (start, end) in range_message_id:
            logger.debug('range(%s, %s)', start, end)
            for current_message_id in range(start, end + 1):
                raw_targets.append((channel_id, current_message_id))
        logger.debug('target: %s', raw_targets)
    else:
        links: list[str] = []

        links = (
            [input('Message link: ')]
            if not args.link
            else [link.strip() for link in args.link.split(';')]
        )
        
        for link in links:
            logger.debug('current link: %s', link)
            channel_id, message_id = link.split('/')[-2:]
            logger.debug('current message_id options: %s', message_id)
            message_id_list: list[str] = []
            range_message_id = utils.parse_ranges(message_id)

            for (start, end) in range_message_id:
                logger.debug('range(%s, %s)', start, end)
                for current_message_id in range(start, end + 1):
                    raw_targets.append((channel_id, current_message_id))
            logger.debug('target: %s', raw_targets)

    output_filename: Optional[str] = args.output_filename

    coros: list[Coroutine[None, None, str]] = []

    for channel_id, message_id in raw_targets:
        updated_channel_id = utils.parse_channel_id(channel_id)
        updated_message_id = utils.parse_message_id(message_id)
        logger.debug('downloading from %s:%s', channel_id,message_id)

        # Get the output filename
        if output_filename is None:
            output_filename = 'file'
        final_output_filename = f'{output_filename}-{channel_id}-{message_id}'
        logger.debug('output filename: %s', final_output_filename)

        coro = rcd_tool.download_media(
            channel_id=updated_channel_id,
            message_id=updated_message_id,
            output_filename=final_output_filename,
            infer_extension=args.infer_extension,
        )
        coros.append(coro)

    tasks = [
        asyncio.ensure_future(coro)
        for coro in coros
    ]
    logger.debug('%d tasks', len(tasks))
    files = rcd_tool.client.loop.run_until_complete(asyncio.gather(*tasks))
    logger.debug('files: %s', files)
    for file in files:
        print(file)
