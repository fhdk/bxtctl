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
from .User import User
from .LogEntry import LogEntry
from .Package import Package
from .Section import Section
from .BxtErrorHandler import BxtErrorHandler
from typing import Dict, Any, List


class HttpResult:
    def __init__(self, json_data: Dict[str, Any], status: int):
        self.json = json_data
        self.status = status

    def get_json(self) -> Dict[str, Any]:
        return self.json

    def get_status(self) -> int:
        return self.status

    def get(self):
        return {
            "json": self.json,
            "status": self.status
        }

    def __str__(self) -> str:
        return f"{self.json}"


class Http:
    """
    Http helper class
    """
    def __init__(self, user_agent: str, access_token: str = None, refresh_token: str = None):
        self._user_agent = user_agent
        self._access_token = access_token
        self._refresh_token = refresh_token

    def make_request(self, url: str, method: str, params=None, data=None) -> HttpResult:
        """
        make http request
        :param url:
        :param method:
        :param params:
        :param data:
        :return:
        """
        session = requests.session()
        session.headers.update({"User-Agent": self._user_agent})

        if self._access_token is not None:
            session.headers.update({"Authorization": "Bearer " + self._access_token})

        try:
            # execute request
            session = session.request(url, method, params=params, json=data)
            # return response data and status
            return HttpResult(session.json(), session.status_code)

        except JSONDecodeError:
            return HttpResult({'error': 'Invalid JSON format'}, 400)

        except requests.exceptions.ConnectionError:
            return HttpResult({'error': 'Connection error'}, 503)

        except requests.exceptions.Timeout:
            return HttpResult({'error': 'Timeout error'}, 408)

    def set_token(self, access_token: str):
        self._access_token = access_token

    def start_sync(self, url: str) -> bool:
        """
        Start sync
        :return: True/False
        """
        try:
            result = self.make_request(url, "POST")
            if result.status == 200:
                return True
        except (Exception,) as err:
            print(f"{err}")
            return False

    def get_logs(self, url) -> [LogEntry]:
        """
        Get package logs
        :param url:
        :return: list of log entries
        """
        try:
            result = self.make_request(url, "GET")
            if result.status == 200:
                return result.json

        except (JSONDecodeError,) as err:
            print(f"{err}")
        except (requests.exceptions.ConnectionError,) as err:
            print(f"{err}")
        except (requests.exceptions.Timeout,) as err:
            print(f"{err}")
        return []

    def get_packages(self, url: str, branch: str, repositoriy: str, architectue: str) -> [Package]:
        """
        get a list of packages
        :param url:
        :param branch:
        :param repositoriy:
        :param architectue:
        :return: [{"name":"string","section","string","repository":"string","branch":"string","architecture":"string"},"pool_entries":[{"version":"string","hasSignature":true}]]]
        """
        try:
            result = self.make_request(url, "GET", params={"branch": branch, "repository": repositoriy,
                                                           "architecture": architectue})
            if result.status == 200:
                return result.json
        except (JSONDecodeError,) as err:
            print(f"{err}")
        except (requests.exceptions.ConnectionError,) as err:
            print(f"{err}")
        except (requests.exceptions.Timeout,) as err:
            print(f"{err}")
        return []

    def get_sections(self, url: str) -> [Section]:
        """
        Get ACL
        :param url:
        :return: [{"branch": "string","repository": "string","architecture": "string"}]
        """
        try:
            result = self.make_request(url, "GET")
            if result.status == 200:
                return result.json
            raise BxtErrorHandler("Section Error", result.json)
        except BxtErrorHandler as e:
            print(f"{e}\n{e.errors}")
        except (JSONDecodeError,) as err:
            print(f"There was an error decoding response from {url}. The message is contained in {err}.")
        except (requests.exceptions.ConnectionError,) as err:
            print(f"{err}")
        return []

    def get_users(self, url: str) -> [User]:
        """
        Get users
        :param url:
        :return: [{"name":"string","permissions":["string"]}]
        """
        try:
            req_result = self.make_request(url, "GET")
            if req_result.status == 200:
                return req_result.json

        except (JSONDecodeError,) as err:
            print(f"{err}")
        except (requests.exceptions.ConnectionError,) as err:
            print(f"{err}")
        return []

    def revoke_refresh_token(self, url: str) -> HttpResult:
        """
        Revoke refresh token
        :param url:
        :return:
        """
        return self.make_request(url, "POST")

    def try_password_token(self, url: str, name: str, passwd: str) -> HttpResult:
        """
        Authenticate from username and password
        :param url:
        :param name:
        :param passwd:
        :return:
        """
        credentials = {"name": name, "password": passwd}
        return self.make_request(url, "POST", data=credentials)

    def try_refresh_token(self, url: str) -> HttpResult:
        """
        Authenticate from refresh token
        :param url:
        :return:
        """
        return self.make_request(url, "POST", data={"token": self._refresh_token})

    def user_add(self, user: User):
        """
        Add user
        :param user:
        :return: 200
        :return: 400
        :return: 401
        """
        pass

    def user_mod(self, user: User):
        """
        Update user
        :param user:
        :return: 200
        :return: 400
        :return: 401
        """
        pass

    def user_del(self, user_id: str):
        """
        Remove user
        :param user_id:
        :return: 200
        :return: 400
        :return: 401
        """
        pass
