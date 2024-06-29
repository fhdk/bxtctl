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
import json
import os
from pwinput import pwinput
from pathlib import Path
from .Http import Http


class BxtConfig:
    """
    Main Settings Class
    """
    license_url = "https://www.gnu.org/licenses/agpl.html"
    app_name = "bxtctl"
    app_version = "0.3.0"
    user_agent = F"{app_name}/{app_version}"
    config_dir = f"{Path.home()}/.config/{app_name}"
    config_file = f"config.json"
    endpoint = {
        "auth": "api/auth",
        "logs": "api/logs/packages",
        "packages": "api/packages",
        "pkgCommit": "api/packages/commit",
        "pkgSnap": "api/packages/snap",
        "pkgSync": "api/packages/sync",
        "sections": "api/sections",
        "user": "api/users",
    }

    def __init__(self):
        """
        Intialize configuration
        Creates the configuration folder and initialize or load configuraiton
        """
        self._file_name = f"{self.config_dir}/{self.config_file}"
        self.http = Http(user_agent=self.user_agent)
        self._url: str = ""
        self._access_token: str = ""
        self._name: str = ""
        self._refresh_token: str = ""

        # create config dir if not existing
        if not os.path.isdir(self.config_dir):
            os.mkdir(self.config_dir)

        if not os.path.isfile(f"{self.config_dir}/{self.config_file}"):
            # generrate empty default
            self.__save_config__()
        else:
            # load config
            self.__load_config__()

    def get_refresh_token(self) -> str:
        """
        Get Refresh Token
        :return:
        """
        return self._refresh_token

    def set_refresh_token(self, token) -> None:
        """
        Set Refresh Token
        :param token:
        :return:
        """
        self._refresh_token = token

    def get_access_token(self) -> str:
        """
        Return Bxt token
        :return:
        """
        return self._access_token

    def set_access_token(self, value: str):
        """
        Set Bxt token
        :param value:
        :return:
        """
        self._access_token = value
        self.__save_config__()

    def get_name(self) -> str:
        """
        Return Bxt username
        :return:
        """
        return self._name

    def set_name(self, value: str):
        """
        Set Bxt username
        :param value:
        :return:
        """
        self._name = value
        self.__save_config__()

    def get_url(self) -> str:
        """
        Return Bxt endpoint url
        :return:
        """
        return self._url

    def set_url(self, value: str):
        """
        Set the Bxt endpoint url
        :param value:
        :return:
        """
        self._url = value
        self.__save_config__()

    def is_valid(self):
        return (self._url is not None and
                self._access_token is not None and
                self._refresh_token is not None and
                self._name is not None)

    def __str__(self):
        """
        Return textual representation of the configuration  class
        :return:
        """
        return f"BxtConfig(Url: '{self._url}', Name: '{self._name}'"

    def __save_config__(self):
        """
        Initialize configuration and write empty config
        :return:
        """
        config = {
            "access_token": self._access_token,
            "refresh_token": self._refresh_token,
            "token_type": self._token_type,
            "name": self._name,
            "url": self._url
        }
        with open(self._file_name, "w") as outfile:
            json.dump(config, outfile)

    def __load_config__(self):
        """
        Load BxtCtl configuration
        The function assumes the file exist
        :return:
        """
        try:
            with open(self._file_name, "r") as infile:
                data = json.load(infile)

            try:
                self._access_token = data["access_token"]
            except (KeyError,) as e:
                self._access_token = ""

            try:
                self._refresh_token = data["refresh_token"]
            except (KeyError,) as e:
                self._refresh_token = ""

            try:
                self._token_type = data["token_type"]
            except (KeyError,) as e:
                self._token_type = ""

            try:
                self._name = data["name"]
            except (KeyError,) as e:
                self._name = ""

            try:
                self._url = f"{data['url']}"
            except (KeyError,) as e:
                self._url = ""

        except (FileNotFoundError,):
            self._token_type = ""
            self._access_token = ""
            self._refresh_token = ""
            self._name = ""
            self._url = ""
        except (Exception,):
            pass

    def configure(self) -> bool:
        """
        Create BctCtl configuration
        :return:
        """
        # get options - username and service url
        options = _get_user_input_for_config()
        # get password from user
        passwd = pwinput(prompt="password: ", mask="")
        # assign options to variables
        self._name = options["name"]
        self._url = options["url"]
        # get response from service
        result = self.http.try_password_token(url=f"{self._url}/{self.endpoint['auth']}",
                                              name=self._name, passwd=passwd)
        if result.status == 200:
            print(result)
            data = result.get_json()
            self._access_token = data["access_token"]
            self._refresh_token = data["refresh_token"]
            self._token_type = data["token_type"]
            exit()

        self.__save_config__()
        if self._access_token == "":
            return False
        return True

    def login(self) -> bool:
        """
        request login credentials to get a token
        :return:
        """
        username = input(f"bxt user ({self._name}): ").strip()
        if username == "":
            username = self._name
        password = pwinput(prompt="password: ", mask="")
        result = self.http.try_password_token(url=f"{self._url}/{self.endpoint['auth']}",
                                              name=username, passwd=password)
        if result.status == 200:
            self._name = username
            self.__save_config__()
            if self._access_token == "":
                return False
            return True

    def revoke_access(self) -> bool:
        result = self.http.revoke_refresh_token(f"{self._url}/{self.endpoint['verify']}")
        if result.status == 200:
            return True
        return False


def _get_user_input_for_config() -> dict:
    """
    get config options from user input
    :return:
    """
    options = {"name": "", "url": ""}
    while True:
        options["url"] = input(f"bxt http: ").strip()
        options["name"] = input(f"bxt user: ").strip()
        if options["url"] != "" and options["name"] != "":
            return options
