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
from .BxtException import BxtException
from .HttpResult import HttpResult
from .LogEntry import LogEntry
from .Package import Package
from .Section import Section
from .User import User


class BxtSession:
    """
    Bxt Http session helper class
    """

    def __init__(self, user_agent: str):
        self._user_agent = user_agent

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

    def commit(self, url: str, data: dict, files: dict, token: str) -> HttpResult:
        """
        post a commit request
        :param url:
        :param data:
        :param files:
        :param token:
        :return: HttpResult
        """
        pass

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
        :return: HttpResult
        """
        session = requests.session()
        if headers is not None:
            session.headers.update(headers)
        session.headers.update({"User-Agent": self._user_agent})

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

    def get_logs(self, url: str, token: str) -> [LogEntry]:
        """
        Get package logs
        :param token:
        :param url:
        :return: list of log entries
        """
        headers = {"Authorization": f"Bearer {token}"}
        result = self.make_http_request(method="get", headers=headers, url=url)
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
        self,
        url: str,
        branch: str,
        repositoriy: str,
        architectue: str,
        token: str,
    ) -> [Package]:
        """
        get a list of packages
        :param token:
        :param url:
        :param branch:
        :param repositoriy:
        :param architectue:
        :return: List of Package
        """
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "branch": branch,
            "repository": repositoriy,
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
