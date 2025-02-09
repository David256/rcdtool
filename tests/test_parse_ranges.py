#!/usr/bin/env python

import rcdtool.utils as utils


def test_solo_range():
    input_string = '344'
    result = utils.parse_ranges(input_string)
    assert len(result) == 1

    assert len(result[0]) == 2

    assert result[0][0] == 344
    assert result[0][1] == 344


def test_simple_range():
    input_string = '1639..1641'
    result = utils.parse_ranges(input_string)
    assert len(result) == 1

    assert len(result[0]) == 2

    assert result[0][0] == 1639
    assert result[0][1] == 1641


def test_complex_range():
    input_string = '1638,1639..1641,1650..1650'
    result = utils.parse_ranges(input_string)
    assert len(result) == 3

    assert len(result[0]) == 2
    assert len(result[1]) == 2
    assert len(result[2]) == 2

    assert result[0][0] == 1638
    assert result[0][1] == 1638

    assert result[1][0] == 1639
    assert result[1][1] == 1641

    assert result[2][0] == 1650
    assert result[2][1] == 1650
