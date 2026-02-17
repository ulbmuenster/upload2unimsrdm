# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 University of Münster.
#
# upload2unimsrdm is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

from upload2unimsrdm import __version__


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"
