# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 University of Münster.
#
# upload2unimsrdm is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

import pytest
from pathlib import Path
from upload2unimsrdm.utils import collect_files, format_size


def test_format_size():
    """Test file size formatting."""
    assert format_size(0) == "0.0 B"
    assert format_size(1023) == "1023.0 B"
    assert format_size(1024) == "1.0 KB"
    assert format_size(1024 * 1024) == "1.0 MB"
    assert format_size(1024 * 1024 * 1024) == "1.0 GB"


def test_collect_files_single_file(tmp_path):
    """Test collecting a single file."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    files = collect_files(test_file)
    assert len(files) == 1
    assert files[0] == test_file


def test_collect_files_directory(tmp_path):
    """Test collecting files from a directory."""
    # Create test files
    (tmp_path / "file1.txt").write_text("content1")
    (tmp_path / "file2.txt").write_text("content2")

    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").write_text("content3")

    files = collect_files(tmp_path)
    assert len(files) == 3
    assert all(f.is_file() for f in files)


def test_collect_files_ignores_hidden(tmp_path):
    """Test that hidden files are ignored."""
    (tmp_path / "visible.txt").write_text("content")
    (tmp_path / ".hidden").write_text("hidden content")

    files = collect_files(tmp_path)
    assert len(files) == 1
    assert files[0].name == "visible.txt"


def test_collect_files_empty_directory(tmp_path):
    """Test collecting from an empty directory."""
    files = collect_files(tmp_path)
    assert len(files) == 0
