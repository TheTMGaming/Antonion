import pytest

from app.internal.services.utils import create_temp_file, remove_temp_file


@pytest.mark.unit
@pytest.mark.parametrize("text", ["12345", "", "       ", "asdfadfs\nasdfsdf", "asdf 123", "\n\n\n\n\n"])
def test_creating_temp_file(text: str) -> None:
    file = create_temp_file(text)

    assert file is not None
    assert file.readable()
    assert file.read() == text


@pytest.mark.unit
def test_removing_temp_file() -> None:
    file = create_temp_file("123")

    remove_temp_file(file)

    assert file.closed
    with pytest.raises(ValueError):
        file.read()
