# -*- coding: utf-8 -*-
#
# bxtctl is command line client designed to interact with bxt api
# bxt can be found at https://gitlab.com/anydistro/bxt
#
# bxtctl is free software: you can redistribute it and/or modify
# it under the terms of the Affero GNU General Public License
# as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# bxtctl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the Affero GNU General Public License
# along with bxtctl.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors: Frede Hundewadt https://github.com/fhdk/bxtctl
#

"""
                            ACHTUNG!
               ALLES CODEMONKEYS UND DEVELOPERS!

Das codemachine ist nicht fuer gefingerpoken und mittengrappen.
You might end up schnappen the crashtest, blowenfusen und debuggen
with the headashbang.

Es ist nicht fuer gevurken by das dumkopfen. Das rubbernecken
sightseeren, und das peering at this file without knowledge macht
bigge troubles und loss of sleepen. Das beste practice ist:
keepen das fingers out of das unkaesslich code unless you know
what you are doing.

Relaxen und trusten das previouser coders, und if du must change,
make sure you commitzen and testzen. If du breaken, fixen it schnell!

                                        ~ The Code Elfen
"""

import logging
from datetime import datetime
import uuid
import requests
from json import JSONDecodeError
from typing import Any
from requests import Request
from requests import RequestException

from Bxt.BxtException import BxtException
from Bxt.HttpResult import HttpResult
from Bxt.LogEntry import LogEntry
from Bxt.Package import Package
from Bxt.Section import Section
from Bxt.User import User


class BxtSession:
    """
    Bxt Http session helper class
    """

    def __init__(self, user_agent: str):
        self._user_agent = user_agent
        logging.getLogger("BxtSession").info("BxtSession initialized")

    def authenticate(self, url: str, username: str, password: str) -> HttpResult:
        """
        Authenticate from username and password
        :param url:
        :param username:
        :param password:
        :return: HttpResult
        """
        data = {"name": username, "password": password, "response_type": "bearer"}
        return self.make_http_request(method="post", url=url, json=data)

    def commit(
        self, url: str, files: dict, token: str, headers: dict = None
    ) -> HttpResult:
        """
        post a commit request
        :param headers:
        :param url:
        :param files:
        :param headers
        :param token:
        :return: HttpResult
        """
        if headers is not None:
            headers.update({"Authorization": f"Bearer {token}"})
        else:
            headers = {"Authorization": f"Bearer {token}"}
        return self.make_http_request(
            method="post", url=url, headers=headers, files=files
        )

    def compare(self, url: str, data: list, token: str) -> HttpResult:
        """
        post compare request
        :param token:
        :param url:
        :param data:
        :return: HttpResult
        """
        headers = {"Authorization": f"Bearer {token}"}
        return self.make_http_request(
            method="post", url=url, headers=headers, json=data
        )

    def make_http_request(
        self,
        method: str,
        url: str,
        data=None,
        files=None,
        headers=None,
        json=None,
        params=None,
    ) -> HttpResult:
        """
        make http request
        :param url: required
        :param method: required
        :param data:
        :param files:
        :param headers:
        :param json:
        :param params:
        :return: HttpResult
        """
        session = requests.session()
        request = Request(
            method=method,
            url=url,
            params=params,
            json=json,
            data=data,
            files=files,
            headers=headers,
        )
        req = request.prepare()
        req.headers.update({"User-Agent": self._user_agent})
        req.headers.update({"X-BxtCtl-Request-Id": str(uuid.uuid4())})

        logging.info(f"BxtSession: Making HTTP request: {method} {url}")
        logging.debug(f"data: {data}")
        logging.debug(f"files: {files}")
        logging.debug(f"headers: {headers}")
        logging.debug(f"json: {json}")
        logging.debug(f"params: {params}")
        try:
            # execute request
            response = session.send(req, stream=True, timeout=30)
            if response.status_code == 200:
                # return response data and status
                return HttpResult(response.json(), response.status_code)
            if response.status_code == 400:
                logging.debug(response.text)
                return HttpResult({"content": "Bad Request"}, response.status_code)
            if response.status_code == 401:
                logging.debug(response.text)
                return HttpResult({"content": "Unauthorized"}, response.status_code)
            if response.status_code == 403:
                logging.debug(response.text)
                return HttpResult({"content": "Forbidden"}, response.status_code)
            if response.status_code == 404:
                logging.debug(response.text)
                return HttpResult(
                    {
                        "content": "Not found",
                    },
                    response.status_code,
                )
            if response.status_code == 408:
                logging.debug(response.text)
                return HttpResult(
                    {
                        "content": "Connection Timeout",
                    },
                    response.status_code,
                )
            if response.status_code == 500:
                logging.debug(response.text)
                return HttpResult(
                    {
                        "content": "Internal Server Error",
                    },
                    response.status_code,
                )
            if response.status_code == 503:
                logging.debug(response.text)
                return HttpResult(
                    {
                        "content": "Connection Error",
                    },
                    response.status_code,
                )

        except RequestException as e:
            return HttpResult({"Internal Server Error": e}, 500)

    def get_logs(self, url: str, params: dict, token: str) -> [LogEntry]:
        """
        Get package logs
        :param params:
        :param token:
        :param url:
        :return: list of log entries
        """
        headers = {"Authorization": f"Bearer {token}"}
        result = self.make_http_request(
            method="get", url=url, headers=headers, params=params
        )
        try:
            if result.status() == 200:
                return result.content()
            raise BxtException(
                "Failed to get logs",
                {"status": result.status(), "message": result.content()},
            )
        except BxtException as e:
            print(f"{e}\n{e.errors}")
        return []

    def get_packages(
        self, url: str, branch: str, repository: str, architectue: str, token: str
    ) -> [Package]:
        """
        get a list of packages
        :param token:
        :param url:
        :param branch:
        :param repository:
        :param architectue:
        :return: List of Package
        """
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "branch": branch,
            "repository": repository,
            "architecture": architectue,
        }
        try:
            result = self.make_http_request(
                method="get", url=url, headers=headers, params=params
            )
            if result.status() == 200:
                return result.content()
            raise BxtException(
                "Failed to get packages",
                {"status": result.status(), "message": result.content()},
            )
        except BxtException as e:
            print(f"{e}\n{e.errors}")
        return []

    def get_sections(self, url: str, token: str) -> [Section]:
        """
        Get ACL
        :param token:
        :param url:
        :return: [{"branch": "string","repository": "string","architecture": "string"}]
        """
        headers = {"Authorization": f"Bearer {token}"}
        try:
            result = self.make_http_request(method="get", url=url, headers=headers)
            if result.status() == 200:
                return result.content()
            raise BxtException(
                "Failed to get sections",
                {"status": result.status(), "message": result.content()},
            )
        except BxtException as e:
            print(f"{e}\n{e.errors}")
        return []

    def get_user(self, url: str, token: str) -> User:
        """
        Get user information
        :param url:
        :param token:
        :return:
        """
        pass

    def revoke_refresh_token(self, url: str, token: str) -> HttpResult:
        """
        Revoke refresh token
        :param token:
        :param url:
        :return: HttpResult
        """
        headers = {"Authorization": f"Bearer {token}"}
        return self.make_http_request(method="post", url=url, headers=headers)

    def use_refresh_token(self, url: str, token: str, refresh_token: str) -> HttpResult:
        """
        Authenticate from refresh token
        :param token:
        :param refresh_token:
        :param url:
        :return: HttpResult
        """
        headers = {"Authorization": f"Bearer {token}"}
        json_data = {"token": refresh_token}
        return self.make_http_request(
            method="get", url=url, headers=headers, json=json_data
        )
