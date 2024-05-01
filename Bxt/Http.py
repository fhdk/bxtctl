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
from requests import utils
import json
from .User import User
from .LogEntry import LogEntry
from .Package import Package


class Http:
    """
    Http helper class
    """
    def __init__(self, user_agent: str, token: str = None):
        self._user_agent = user_agent
        self._token = token

    def set_token(self, token: str):
        self._token = token

    def get_logs(self, url) -> [LogEntry]:
        """
        Get package logs
        :param url:
        :return:[{
                    "id": "string",
                    "time": "string",
                    "package": {
                        "name": "string",
                        "section": {
                            "branch": "string",
                            "repository": "string",
                            "architecture": "string"
                        }, "pool_entries":
                        [
                            {
                                "version": "string",
                                "hasSignature": true
                            }
                        ]
                    },
                    "action": "string"
                }]
        """
        session = self._http_prepare_session()
        session = session.get(url)
        return json.loads(session.text)

    def get_packages(self, url: str, branch: str, repositoriy: str, architectue: str) -> [Package]:
        """
        get a list of packages
        :param url:
        :param branch:
        :param repositoriy:
        :param architectue:
        :return: 200 [{"name":"string","section","string","repository":"string","branch":"string","architecture":"string"},"pool_entries"[{"version":"string","hasSignature":true}]]]
        :return: 401
        """
        session = self._http_prepare_session()
        session = session.get(url, params={"branch": branch, "repository": repositoriy, "architecture": architectue})
        return json.loads(session.text)

    def get_sections(self, url: str) -> list:
        """
        Get ACL
        :param url:
        :return: 200 [{"branch": "string","repository": "string","architecture": "string"}]
        :return: 401
        """
        try:
            session = self._http_prepare_session()
            session = session.get(url)
            return json.loads(session.text)

        except (requests.exceptions.ConnectionError,) as err:
            print(f"{err}")

        return []

    def get_users(self, url: str) -> [User]:
        """
        Get users
        :param url:
        :return: 200 [{"name":"string","permissions":["string"]}]
        :return: 401
        """
        try:
            session = self._http_prepare_session()
            session = session.get(url)
            return json.loads(session.txt)
        except (requests.exceptions.ConnectionError,) as err:
            print(f"{err}")

    def add_user(self, user: User):
        """
        Add user
        :param user:
        :return: 200
        :return: 400
        :return: 401
        """
        pass

    def update_user(self, user: User):
        """
        Update user
        :param user:
        :return: 200
        :return: 400
        :return: 401
        """

    def remove_user(self, user_id: str):
        """
        Remove user
        :param user_id:
        :return: 200
        :return: 400
        :return: 401
        """
        pass

    def verify_token(self, url: str) -> bool:
        """
        Verify the class token
        :param url:
        :return: 200 {"status":"ok"}
        :return: 401
        """
        try:
            session = self._http_prepare_session()
            session = session.get(url)
            if session.status_code == 200:
                return True

        except (Exception,) as e:
            print(e)

        return False

    def get_token(self, url: str, name: str, passwd: str) -> str:
        """
        request a token using credentials
        :param url:
        :param name:
        :param passwd:
        :return: 200 { "token":"<string>" }
        :return: 401
        """
        credentials = {"name": name, "password": passwd}
        try:
            session = self._http_prepare_session()
            session = session.post(url, json=credentials)
            if session.status_code == 200:
                cookie_jar = requests.utils.dict_from_cookiejar(session.cookies)
                try:
                    token = cookie_jar["token"]
                    self._token = token
                    return token
                except (KeyError,):
                    print("CookieJar is empty :(")
        except (Exception,) as err:
            print(err)
        return ""

    def _http_prepare_session(self) -> requests.session():
        """
        prepare the http session
        :return:
        """
        session = requests.session()
        session.headers.update({"User-Agent": self._user_agent})
        if self._token is not None:
            session.cookies.update({"token": self._token})
        return session
