# -*- coding: utf-8 -*-

from upload2unimsrdm.cli import is_archive_file


def test_is_archive_file_detects_zip_signature_with_non_archive_suffix(tmp_path):
    file_path = tmp_path / "payload.bin"
    file_path.write_bytes(b"PK\x03\x04" + b"dummy")

    assert is_archive_file(file_path) is True


def test_is_archive_file_rejects_spoofed_zip_extension(tmp_path):
    file_path = tmp_path / "not_archive.zip"
    file_path.write_text("plain text file", encoding="utf-8")

    assert is_archive_file(file_path) is False


def test_is_archive_file_detects_tar_signature_at_header_offset(tmp_path):
    file_path = tmp_path / "archive.data"
    header = bytearray(512)
    header[257:262] = b"ustar"
    file_path.write_bytes(header)

    assert is_archive_file(file_path) is True
