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
from typing import cast, Union, Optional

import configparser
import filetype
from telethon import TelegramClient
import telethon.functions as functions
from telethon.functions import channels
import telethon.types as tg_types

from rcdtool.log import logger


class RCD:
    def __init__(self, config_filename: str, dry_mode: Optional[bool] = None):
        self.config_filename = config_filename
        self.config = self.get_config(self.config_filename)
        self.client = self.create_client()
        self.dry_mode = dry_mode

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
        # Optional tuning knobs with sensible defaults
        timeout = int(self.config['Client'].get('timeout', '7000'))
        device_model = self.config['Client'].get('device_model', 'scriptgram')
        lang_code = self.config['Client'].get('lang_code', 'en-US')
        request_retries = int(self.config['Client'].get('request_retries', '5'))
        retry_delay = int(self.config['Client'].get('retry_delay', '2'))
        connection_retries = int(self.config['Client'].get('connection_retries', '5'))

        client = TelegramClient(
            session=self.config['Access']['session'],
            api_id=int(self.config['Access']['id']),
            api_hash=self.config['Access']['hash'],
            timeout=timeout,
            device_model=device_model,
            lang_code=lang_code,
            request_retries=request_retries,
            retry_delay=retry_delay,
            connection_retries=connection_retries,
        )
        client.start()
        return client

    async def download_media(self,
                      channel_id: Union[int, str],
                      message_id: int,
                      output_filename: str,
                      infer_extension: Optional[bool] = None,
                      workers: Optional[int] = None,
                      part_size_kb: Optional[int] = None,
                      discussion_message_id: Optional[int] = None,
                      ):
        """Read a message in a channel and download the media to output.

        Args:
            client (TelegramClient): The Telegram client object.
            channel_id (int): The channel ID.
            message_id (int): The message ID.
            output_filename (str): The output filename.
        """
        if self.dry_mode:
            logger.info('dry running')

        try:
            entity = await self.client.get_entity(channel_id)
            if not isinstance(entity, tg_types.Channel):
                logger.warning('Cannot get a Channel object from that channel id')
                return
            if entity.access_hash is None:
                logger.warning('Cannot get the access hash for that channel')
                return

            input_channel = tg_types.InputChannel(entity.id, entity.access_hash)

            id = tg_types.InputMessageID(message_id)

            messages_request = channels.GetMessagesRequest(input_channel, [id])
            channel_messages = await self.client(messages_request)
            if not isinstance(channel_messages, tg_types.messages.ChannelMessages):
                logger.warning('Cannot continue because the got type is not a ChannelMessages')
                return

            message = channel_messages.messages[0]
            if not isinstance(message, tg_types.Message):
                logger.warning('Cannot continue because the got type is not a Message')
                return

            # defer logging until we finalize the target message

            if discussion_message_id:
                logger.info('finding message from a discussion group')
                if message.replies and message.replies.comments:
                    input_peer = await self.client.get_input_entity(message.peer_id)
                    request = functions.messages.GetDiscussionMessageRequest(
                        peer=input_peer,
                        msg_id=message.id,
                    )
                    discussion_message = await self.client(request)
                    if not isinstance(discussion_message, tg_types.messages.DiscussionMessage):
                        logger.warning('Cannot get the discussion message')
                        return

                    comment_message = discussion_message.messages[0]
                    if comment_message.peer_id is None:
                        logger.warning('Found a discussion message peer id as none')
                        return

                    entity = await self.client.get_entity(
                        comment_message.peer_id,
                    )
                    if not isinstance(entity, tg_types.Channel):
                        logger.warning('Cannot get a Channel object from the discussion message id')
                        return
                    if entity.access_hash is None:
                        logger.warning('Cannot get the access hash for that channel')
                        return
                    
                    input_channel = tg_types.InputChannel(entity.id, entity.access_hash)
                    id = tg_types.InputMessageID(discussion_message_id)
                    messages_request = channels.GetMessagesRequest(input_channel, [id])
                    channel_messages = await self.client(messages_request)
                    if not isinstance(channel_messages, tg_types.messages.ChannelMessages):
                        logger.warning('Cannot continue because the got type is not a ChannelMessages from the discussion channel')
                        return
                    # overwrite the object message
                    message = channel_messages.messages[0]
                    if not isinstance(message, tg_types.Message):
                        logger.warning('Cannot continue because the got type is not a Message  from the discussion channel')
                        return
                else:
                    logger.error('message with no comments')
                    return

            if self.dry_mode:
                return output_filename

            # Try to compute and log media size (when available) before download
            def _fmt_bytes(n: int | float) -> tuple[float, str]:
                units = ['B', 'KB', 'MB', 'GB', 'TB']
                val = float(n)
                idx = 0
                while val >= 1024.0 and idx < len(units) - 1:
                    val /= 1024.0
                    idx += 1
                return val, units[idx]

            def _get_media_size(m) -> Optional[int]:
                try:
                    if isinstance(m, tg_types.MessageMediaDocument) and isinstance(m.document, tg_types.Document):
                        return int(getattr(m.document, 'size', 0) or 0) or None
                    if isinstance(m, tg_types.MessageMediaPhoto) and isinstance(m.photo, tg_types.Photo):
                        sizes = getattr(m.photo, 'sizes', []) or []
                        candidates = [getattr(s, 'size', None) for s in sizes]
                        candidates = [int(x) for x in candidates if isinstance(x, int)]
                        return max(candidates) if candidates else None
                    if isinstance(m, tg_types.MessageMediaPaidMedia):
                        total = 0
                        found = False
                        for em in m.extended_media:
                            if isinstance(em, tg_types.MessageExtendedMedia):
                                inner = em.media
                                if isinstance(inner, tg_types.Document):
                                    total += int(getattr(inner, 'size', 0) or 0)
                                    found = True
                                elif isinstance(inner, tg_types.Photo):
                                    sizes = getattr(inner, 'sizes', []) or []
                                    candidates = [getattr(s, 'size', None) for s in sizes]
                                    candidates = [int(x) for x in candidates if isinstance(x, int)]
                                    if candidates:
                                        total += max(candidates)
                                        found = True
                        return total if found else None
                except Exception:
                    return None
                return None

            pre_media = message.media
            pre_size = _get_media_size(pre_media)
            if pre_size:
                s_val, s_unit = _fmt_bytes(pre_size)
                logger.info('size: %.2f %s', s_val, s_unit)
            logger.info('downloading...')

            media = message.media
            if media is None:
                logger.warning('No media found')
                return

            # Resolve defaults from config if not provided
            cfg_workers = int(self.config['Client'].get('workers', '4'))
            cfg_part_kb = int(self.config['Client'].get('part_size_kb', '512'))

            # Throttle logs: progress callback every ~1s
            import time
            last_t = 0.0
            last_b = 0

            def _fmt_bytes(n: int | float) -> tuple[float, str]:
                units = ['B', 'KB', 'MB', 'GB', 'TB']
                val = float(n)
                idx = 0
                while val >= 1024.0 and idx < len(units) - 1:
                    val /= 1024.0
                    idx += 1
                return val, units[idx]

            def _progress(bytes_downloaded: int, total: Optional[int]):
                nonlocal last_t, last_b
                now = time.time()
                if last_t == 0.0:
                    last_t, last_b = now, bytes_downloaded
                    return
                if now - last_t >= 1.0:
                    delta_b = bytes_downloaded - last_b
                    speed = delta_b / (now - last_t)
                    spd_val, spd_unit = _fmt_bytes(speed)
                    cur_val, cur_unit = _fmt_bytes(bytes_downloaded)
                    if total:
                        tot_val, tot_unit = _fmt_bytes(total)
                        percent = bytes_downloaded * 100 / total
                        logger.info('progress: %.2f %s/%.2f %s (%.1f%%) at %.2f %s',
                                    cur_val, cur_unit, tot_val, tot_unit, percent, spd_val, spd_unit)
                    else:
                        logger.info('progress: %.2f %s at %.2f %s', cur_val, cur_unit, spd_val, spd_unit)
                    last_t, last_b = now, bytes_downloaded

            # Use low-level download_file for broad Telethon compatibility and control
            import inspect

            async def _dl_file(input_media, out_path: str):
                sig = None
                try:
                    sig = inspect.signature(self.client.download_file)
                except Exception:
                    sig = None

                kwargs = {
                    'file': out_path,
                    'part_size_kb': part_size_kb or cfg_part_kb,
                    'progress_callback': _progress,
                }
                # Add workers only if supported in this Telethon version
                if sig and 'workers' in sig.parameters:
                    if workers or cfg_workers:
                        kwargs['workers'] = workers or cfg_workers

                try:
                    await self.client.download_file(input_media, **kwargs)
                except TypeError:
                    # Fallback: remove optional kwargs progressively
                    kwargs.pop('progress_callback', None)
                    try:
                        await self.client.download_file(input_media, **kwargs)
                    except TypeError:
                        kwargs.pop('part_size_kb', None)
                        kwargs.pop('workers', None)
                        await self.client.download_file(input_media, **kwargs)

            if isinstance(media, tg_types.MessageMediaPaidMedia):
                logger.debug('paid message found')
                for message_extended_media in media.extended_media:
                    if isinstance(message_extended_media, tg_types.MessageExtendedMedia):
                        await _dl_file(message_extended_media.media, output_filename)
                    else:
                        logger.warning('Cannot find a message extended media')
                        return
                logger.info('downloaded to %s', output_filename)
            else:
                await _dl_file(media, output_filename)
                logger.info('downloaded to %s', output_filename)

                if infer_extension:
                    result = filetype.guess(output_filename)
                    if result:
                        ext = result.extension
                        new_output_filename = f'{output_filename}.{ext}'
                        os.rename(output_filename, new_output_filename)
                        logger.debug('rename to %s', new_output_filename)
                        return new_output_filename
                return output_filename
        except Exception as err:
            logger.error('Error: channel_id=%s, message_id=%s, output_filename=%s, infer_extension=%s',
                         channel_id,
                         message_id,
                         output_filename,
                         infer_extension)
            logger.error(err)
