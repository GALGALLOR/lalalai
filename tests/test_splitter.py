import pytest
from tools.api.lalalai_splitter import make_content_disposition, get_filename_from_content_disposition


def test_make_content_disposition_ascii():
    header = make_content_disposition("file.txt")
    assert header == 'attachment; filename="file.txt"'


def test_make_content_disposition_unicode():
    name = 'файл.txt'
    header = make_content_disposition(name)
    assert header.startswith('attachment; filename*=utf-8\'\'')
    # Check that encoded part matches quoted
    encoded_part = header.split("''", 1)[1]
    from urllib.parse import unquote
    assert unquote(encoded_part) == name


def test_get_filename_from_content_disposition_ascii():
    header = 'attachment; filename="test.txt"'
    assert get_filename_from_content_disposition(header) == 'test.txt'


def test_get_filename_from_content_disposition_unicode():
    name = 'пример.txt'
    from urllib.parse import quote
    header = f"attachment; filename*=utf-8''{quote(name)}"
    assert get_filename_from_content_disposition(header) == name


def test_get_filename_from_content_disposition_invalid():
    with pytest.raises(ValueError):
        get_filename_from_content_disposition('attachment')
