from __future__ import annotations

from http import HTTPStatus

import pytest
from django.urls import reverse

from credit_clear.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_register_returns_user_and_tokens(client):
    url = reverse("users_api:register")
    payload = {
        "email": "newuser@example.com",
        "password": "A-very-strong-password-123!",
        "name": "New User",
        "terms_accepted": True,
        "privacy_accepted": True,
    }
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == HTTPStatus.CREATED
    body = response.json()
    assert body["user"]["email"] == "newuser@example.com"
    assert "access_token" in body["tokens"]
    assert "refresh_token" in body["tokens"]


def test_login_and_me_flow(client):
    password = "Strong-pass-123!"
    user = UserFactory.create(email="member@example.com", password=password)
    login_response = client.post(
        reverse("users_api:login"),
        {"email": user.email, "password": password},
        content_type="application/json",
    )
    assert login_response.status_code == HTTPStatus.OK
    access_token = login_response.json()["tokens"]["access_token"]

    me_response = client.get(
        reverse("users_api:me"),
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_response.status_code == HTTPStatus.OK
    assert me_response.json()["email"] == user.email


def test_refresh_rotates_tokens(client):
    password = "Strong-pass-123!"
    user = UserFactory.create(email="rotate@example.com", password=password)
    login_response = client.post(
        reverse("users_api:login"),
        {"email": user.email, "password": password},
        content_type="application/json",
    )
    refresh_token = login_response.json()["tokens"]["refresh_token"]

    refresh_response = client.post(
        reverse("users_api:token_refresh"),
        {"refresh_token": refresh_token},
        content_type="application/json",
    )
    assert refresh_response.status_code == HTTPStatus.OK
    assert refresh_response.json()["tokens"]["refresh_token"] != refresh_token
