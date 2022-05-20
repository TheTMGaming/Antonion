from typing import Callable
from unittest.mock import MagicMock

import pytest
from django.http import HttpRequest


@pytest.fixture(scope="function")
def get_response() -> Callable:
    get_response = MagicMock()
    get_response.return_value = None

    return get_response


@pytest.fixture(scope="function")
def http_request() -> HttpRequest:
    request = MagicMock()
    request.headers = {}

    return request
