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

"""
Some things for the logging
"""
import logging
from colored import Fore, Style, Back

CODENAME = 'rcdtool'


TAG = f'[{Fore.blue}{CODENAME}{Style.reset}]'
INFO_TAG = f'[{Fore.cyan}info{Style.reset}]'
WARN_TAG = f'[{Fore.yellow}warn{Style.reset}]'
ERROR_TAG = f'[{Fore.red}error{Style.reset}]'
CRITICAL_TAG = f'[{Fore.magenta}critical{Style.reset}]'
DEBUG_TAG = f'[{Fore.light_green}debug{Style.reset}]'


class ColoredFormatter(logging.Formatter):
    """
    ColoredFormatter class.
    """

    def format(self, record):
        """Apply a format to a message.

        Args:
            record (LogRecord): The log record.
        """
        message = record.getMessage()
        name = f'{Fore.light_gray}{Back.cyan} {record.name} {Style.reset}'

        tag = '[log]'

        text_message = f'{message}'

        if record.levelname == 'INFO':
            tag = INFO_TAG
            text_message = f'{Style.italic}{message}{Style.reset}'
        elif record.levelname == 'WARNING':
            tag = WARN_TAG
            text_message = f'{Style.underline}{message}{Style.reset}'
        elif record.levelname == 'ERROR':
            tag = ERROR_TAG
            text_message = f'{Style.blink}{Fore.light_red}{message}{Style.reset}'
        elif record.levelname == 'CRITICAL':
            tag = CRITICAL_TAG
            text_message = f'{Back.light_red}{message}{Style.reset}'
        elif record.levelname == 'DEBUG':
            tag = DEBUG_TAG
            text_message = f'{Fore.dark_gray}{message}{Style.reset}'
        else:
            text_message = f'{message}'

        text = f'{name} {tag}'

        text += f' {text_message}'

        return text


class RCDToolLogger(logging.getLoggerClass()):
    """RCDToolLogger"""
    def __init__(self, name: str, level: int | str = 0) -> None:
        super().__init__(name, level)
        formatter = ColoredFormatter()
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.addHandler(handler)


logger = RCDToolLogger(CODENAME)
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    logger.info('info')
    logger.debug('debug')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')
