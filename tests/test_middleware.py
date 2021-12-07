# Copyright (c) 2021, VRAI Labs and/or its affiliates. All rights reserved.
#
# This software is licensed under the Apache License, Version 2.0 (the
# "License") as published by the Apache Software Foundation.
#
# You may not use this file except in compliance with the License. You may
# obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest import fixture
from pytest import mark

from supertokens_python import init
from supertokens_python.recipe import session, emailpassword
from supertokens_python.framework.fastapi import Middleware
from tests.utils import (
    reset, setup_st, clean_st, start_st
)


def setup_function(f):
    reset()
    clean_st()
    setup_st()


def teardown_function(f):
    reset()
    clean_st()


@fixture(scope='function')
async def driver_config_client():
    app = FastAPI()
    app.add_middleware(Middleware)
    return TestClient(app)


@mark.asyncio
async def test_rid_with_session_and_non_existant_api_in_session_recipe_gives_404(driver_config_client: TestClient):
    init({
        'supertokens': {
            'connection_uri': "http://localhost:3567",
        },
        'framework': 'fastapi',
        'app_info': {
            'app_name': "SuperTokens Demo",
            'api_domain': "http://api.supertokens.io",
            'website_domain': "supertokens.io"
        },
        'recipe_list': [session.init({}), emailpassword.init({})],
    })
    start_st()

    response = driver_config_client.post(
        url='/auth/signin',
        headers={
            "rid": "session"
        })
    assert response.status_code == 404


@mark.asyncio
async def test_no_rid_with_existent_API_does_not_give_404(driver_config_client: TestClient):
    init({
        'supertokens': {
            'connection_uri': "http://localhost:3567",
        },
        'framework': 'fastapi',
        'app_info': {
            'app_name': "SuperTokens Demo",
            'api_domain': "http://api.supertokens.io",
            'website_domain': "supertokens.io"
        },
        'recipe_list': [session.init({}), emailpassword.init({})],
    })
    start_st()

    response = driver_config_client.post(
        url='/auth/signin')
    assert response.status_code == 400


@mark.asyncio
async def test_rid_as_anticsrf_with_existent_API_does_not_give_404(driver_config_client: TestClient):
    init({
        'supertokens': {
            'connection_uri': "http://localhost:3567",
        },
        'framework': 'fastapi',
        'app_info': {
            'app_name': "SuperTokens Demo",
            'api_domain': "http://api.supertokens.io",
            'website_domain': "supertokens.io"
        },
        'recipe_list': [session.init({}), emailpassword.init({})],
    })
    start_st()

    response = driver_config_client.post(
        url='/auth/signin',
        headers={
            "rid": "anti-csrf"
        })
    assert response.status_code == 400


@mark.asyncio
async def test_random_rid_with_existent_API_does_gives_404(driver_config_client: TestClient):
    init({
        'supertokens': {
            'connection_uri': "http://localhost:3567",
        },
        'framework': 'fastapi',
        'app_info': {
            'app_name': "SuperTokens Demo",
            'api_domain': "http://api.supertokens.io",
            'website_domain': "supertokens.io"
        },
        'recipe_list': [session.init({}), emailpassword.init({})],
    })
    start_st()

    response = driver_config_client.post(
        url='/auth/signin',
        headers={
            "rid": "random"
        })
    assert response.status_code == 404