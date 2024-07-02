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

import requests
from json import JSONDecodeError
from .HttpResult import HttpResult
from .LogEntry import LogEntry
from .Package import Package
from .Section import Section
from .BxtException import BxtException


class Http:
    """
    Http helper class
    """

    def __init__(self, user_agent: str, access_token: str = None):
        self._user_agent = user_agent
        self._access_token: str = access_token

    def authenticate(self, url: str, username: str, password: str) -> HttpResult:
        """
        Authenticate from username and password
        :param url:
        :param username:
        :param password:
        :return:
        """
        data = {"name": username, "password": password, "response_type": "bearer"}
        return self.make_http_request(method="post", url=url, json=data)

    def commit(self, url: str, data: list, files: list) -> HttpResult:
        """
        post a commit request
        :return:
        """
        pass

    def compare(self, url: str, data: list) -> HttpResult:
        """
        post compare request
        :param url:
        :param data:
        :return:
        """
        return self.make_http_request(method="post", url=url, json=data)
        # {
        #     "pkgSection": [
        #         {
        #             "branch": "unstable",
        #             "repository": "core",
        #             "architecture": "x86_64"
        #         },
        #         {
        #             "branch": "testing",
        #             "repository": "core",
        #             "architecture": "x86_64"
        #         },
        #         {
        #             "branch": "stable",
        #             "repository": "core",
        #             "architecture": "x86_64"
        #         }
        #     ],
        #     "compareTable": {
        #         "qwt": {
        #             "unstable/core/x86_64": {
        #                 "overlay": "6.2.0-1"
        #             },
        #             "testing/core/x86_64": {
        #                 "overlay": "6.2.0-1"
        #             },
        #             "stable/core/x86_64": {
        #                 "overlay": "6.2.0-1"
        #             }
        #         }
        #     }
        # }

    def make_http_request(
        self,
        method: str,
        url: str,
        params=None,
        json=None,
        data=None,
        headers=None,
        files=None,
    ) -> HttpResult:
        """
        make http request
        :param files:
        :param headers:
        :param data:
        :param url:
        :param method:
        :param params:
        :param json:
        :return:
        """
        session = requests.session()
        if headers is not None:
            session.headers.update(headers)
        session.headers.update({"User-Agent": self._user_agent})

        if self._access_token is not None:
            # todo - check for expiration and refresh if required
            session.headers.update({"Authorization": "Bearer " + self._access_token})

        try:
            # execute request
            session = session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                data=data,
                files=files,
                headers=headers,
            )
            # return response data and status
            return HttpResult(session.json(), session.status_code)

        except JSONDecodeError:
            return HttpResult({"error": "Invalid JSON format"}, 400)

        except requests.exceptions.ConnectionError:
            return HttpResult({"error": "Connection error"}, 503)

        except requests.exceptions.Timeout:
            return HttpResult({"error": "Timeout error"}, 408)

    def get_logs(self, url: str) -> [LogEntry]:
        """
        Get package logs
        :param url:
        :return: list of log entries
        """
        result = self.make_http_request(method="get", url=url)
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
        self, url: str, branch: str, repositoriy: str, architectue: str
    ) -> [Package]:
        """
        get a list of packages
        :param url:
        :param branch:
        :param repositoriy:
        :param architectue:
        :return:
        """
        params = {
            "branch": branch,
            "repository": repositoriy,
            "architecture": architectue,
        }
        try:
            result = self.make_http_request(method="get", url=url, params=params)
            if result.status() == 200:
                return result.content()
            raise BxtException(
                "Failed to get packages",
                {"status": result.status(), "message": result.content()},
            )
        except BxtException as e:
            print(f"{e}\n{e.errors}")
        return []

    def get_sections(self, url: str) -> [Section]:
        """
        Get ACL
        :param url:
        :return: [{"branch": "string","repository": "string","architecture": "string"}]
        """
        try:
            result = self.make_http_request(method="get", url=url)
            if result.status() == 200:
                return result.content()
            raise BxtException(
                "Failed to get sections",
                {"status": result.status(), "message": result.content()},
            )
        except BxtException as e:
            print(f"{e}\n{e.errors}")
        return []

    def renew_access_token(self, url: str, refresh_token: str) -> HttpResult:
        """
        Authenticate from refresh token
        :param refresh_token:
        :param url:
        :return:
        """
        data = {"token": refresh_token}
        return self.make_http_request(method="get", url=url, json=data)

    def revoke_refresh_token(self, url: str) -> HttpResult:
        """
        Revoke refresh token
        :param url:
        :return:
        """
        return self.make_http_request(method="post", url=url)

    def set_access_token(self, access_token: str):
        """
        set access token
        :param access_token:
        :return:
        """
        self._access_token = access_token
