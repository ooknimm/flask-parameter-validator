from typing import Annotated

import pytest
from flask import Flask, jsonify

from flask_parameter_validator import Path, parameter_validator
from tests.conftest import User

app = Flask(__name__)
client = app.test_client()


@app.put("/users/<user_id>")
@parameter_validator
def put_user(user_id: Annotated[int, Path()], user: User):
    return jsonify({"user_id": user_id, **user.model_dump()})


@app.post("/greater_than/<user_id>")
@parameter_validator
def greater_than(user_id: Annotated[int, Path(gt=10)]):
    return jsonify({"user_id": user_id})


@pytest.mark.parametrize(
    "path,body,expected_status,expected_response",
    [
        (
            "/users/1",
            {"name": "nick", "address": "seoul"},
            200,
            {"user_id": 1, "name": "nick", "address": "seoul"},
        ),
        (
            "/users/first",
            {"name": "nick", "address": "seoul"},
            422,
            {
                "detail": [
                    {
                        "type": "int_parsing",
                        "loc": ["path", "user_id"],
                        "msg": "Input should be a valid integer, unable to parse string as an integer",
                        "input": "first",
                        "url": "https://errors.pydantic.dev/2.1.2/v/int_parsing",
                    }
                ]
            },
        ),
    ],
)
def test_path_params(path, body, expected_status, expected_response):
    response = client.put(path, json=body)
    assert response.status_code == expected_status
    assert response.get_json() == expected_response


@pytest.mark.parametrize(
    "path,body,expected_status,expected_response",
    [
        (
            "/greater_than/100",
            {},
            200,
            {"user_id": 100},
        ),
        (
            "/greater_than/1",
            {},
            422,
            {
                "detail": [
                    {
                        "type": "greater_than",
                        "ctx": {"gt": 10},
                        "input": "1",
                        "loc": ["path", "user_id"],
                        "msg": "Input should be greater than 10",
                        "url": "https://errors.pydantic.dev/2.1.2/v/greater_than",
                    }
                ]
            },
        ),
    ],
)
def test_greater_than_path_params(path, body, expected_status, expected_response):
    response = client.post(path, json=body)
    assert response.status_code == expected_status
    assert response.get_json() == expected_response
