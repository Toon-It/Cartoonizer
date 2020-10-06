import pytest
import requests

from http import HTTPStatus

def test_status():
    r = requests.get('http://localhost:5000/')
    assert r.status_code == HTTPStatus.OK
