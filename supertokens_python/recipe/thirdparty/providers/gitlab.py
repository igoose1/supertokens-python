# Copyright (c) 2023, VRAI Labs and/or its affiliates. All rights reserved.
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

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Dict, List, Union

from supertokens_python.normalised_url_domain import NormalisedURLDomain

from httpx import AsyncClient
from supertokens_python.recipe.thirdparty.provider import Provider
from supertokens_python.recipe.thirdparty.types import (
    AccessTokenAPI,
    AuthorisationRedirectAPI,
    UserInfo,
    UserInfoEmail,
)

if TYPE_CHECKING:
    from supertokens_python.framework.request import BaseRequest


class GitLab(Provider):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scope: Union[None, List[str]] = None,
        authorisation_redirect: Union[
            None, Dict[str, Union[str, Callable[[BaseRequest], str]]]
        ] = None,
        gitlab_base_url: str = "https://gitlab.com",
        is_default: bool = False,
    ):
        super().__init__("gitlab", is_default)
        default_scopes = ["read_user"]
        if scope is None:
            scope = default_scopes
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = list(set(scope))
        gitlab_base_url = NormalisedURLDomain(gitlab_base_url).get_as_string_dangerous()
        self.gitlab_base_url = gitlab_base_url
        self.access_token_api_url = f"{gitlab_base_url}/oauth/token"
        self.authorisation_redirect_url = f"{gitlab_base_url}/oauth/authorize"
        self.authorisation_redirect_params = {}
        if authorisation_redirect is not None:
            self.authorisation_redirect_params = authorisation_redirect

    async def get_profile_info(
        self, auth_code_response: Dict[str, Any], user_context: Dict[str, Any]
    ) -> UserInfo:
        access_token: str = auth_code_response["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        async with AsyncClient() as client:
            response = await client.get(f"{self.gitlab_base_url}/api/v4/user", headers=headers)  # type: ignore
            user_info = response.json()
            user_id = str(user_info["id"])
            email = user_info.get("email")
            if email is None:
                return UserInfo(user_id)
            is_email_verified = user_info.get("confirmed_at") is not None
            return UserInfo(user_id, UserInfoEmail(email, is_email_verified))

    def get_authorisation_redirect_api_info(
        self, user_context: Dict[str, Any]
    ) -> AuthorisationRedirectAPI:
        params = {
            "scope": " ".join(self.scopes),
            "response_type": "code",
            "client_id": self.client_id,
            **self.authorisation_redirect_params,
        }
        return AuthorisationRedirectAPI(self.authorisation_redirect_url, params)

    def get_access_token_api_info(
        self,
        redirect_uri: str,
        auth_code_from_request: str,
        user_context: Dict[str, Any],
    ) -> AccessTokenAPI:
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": auth_code_from_request,
            "redirect_uri": redirect_uri,
        }
        return AccessTokenAPI(self.access_token_api_url, params)

    def get_redirect_uri(self, user_context: Dict[str, Any]) -> Union[None, str]:
        return None

    def get_client_id(self, user_context: Dict[str, Any]) -> str:
        return self.client_id
