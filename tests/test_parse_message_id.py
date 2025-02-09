#!/usr/bin/env python

import pytest
import rcdtool.utils as utils


def test_parse_message_id_from_number():
    message_id = 1000
    result = utils.parse_message_id(message_id)
    assert isinstance(result, int)
    assert result == message_id


def test_parse_message_id_from_number_string():
    message_id = '1000'
    result = utils.parse_message_id(message_id)
    assert isinstance(result, int)
    assert f'{result}' == message_id


def test_parse_raise_error():
    message_id = '200OK'
    with pytest.raises(ValueError):
        utils.parse_message_id(message_id)
