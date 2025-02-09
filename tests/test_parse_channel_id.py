#!/usr/bin/env python

import rcdtool.utils as utils


def test_parse_channel_id_from_number():
    channel_id = 300020001000
    result = utils.parse_channel_id(channel_id)
    assert isinstance(result, int), f'"{result}" is not an integer'
    assert result < 0, f'"{result}" is not a negative number'


def test_parse_channel_id_from_negative_number():
    channel_id = -10001000
    result = utils.parse_channel_id(channel_id)
    assert isinstance(result, int), f'"{result}" is not an integer'
    assert result < 0, f'"{result}" is not a negative number'


def test_parse_channel_id_from_string_number():
    channel_id = '400300200100'
    result = utils.parse_channel_id(channel_id)
    assert isinstance(result, int), f'"{result}" is not an integer'
    assert result < 0, f'"{result}" is not a negative number'

def test_parse_channel_id_from_public_link():
    channel_id = '@qwerty'
    result = utils.parse_channel_id(channel_id)
    assert isinstance(result, str)
    assert f'@{result}' == channel_id
