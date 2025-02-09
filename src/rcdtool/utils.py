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

from typing import Union

def parse_channel_id(channel_id: Union[str, int]):
    """Parse the channel id.
    
    This can be string (@public_link) or int (for private channel).
    Also, the private channel id should be negative number.

    Args:
        channel_id (Union[str, int]): The channel id.

    Returns:
        Union[str, int]: The channel id.
    """
    if isinstance(channel_id, str):
        if channel_id.isdigit():
            channel_id = int(channel_id)
        else:
            channel_id = channel_id.replace('@', '')

    # for channel, the ID are negatives
    if isinstance(channel_id, int) and channel_id > 0:
        channel_id = int(f'-100{channel_id}')
    # return that
    return channel_id


def parse_message_id(message_id: Union[str, int]):
    """Parse to integer the message id.

    Args:
        message_id (Union[str, int]): The message id.

    Returns:
        int: The channel id as an integer object.
    """
    if isinstance(message_id, str):
        message_id = int(message_id)
    return message_id

