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


class Config:
    """
    Main Settings Class
    """
    license_url = "https://www.gnu.org/licenses/agpl.html"
    app_name = "bxtctl"
    app_version = "0.2.0"
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
        "verify": "api/verify",
        "user": "api/users",
        "userAdd": "api/users/add",
        "userUpdate": "api/users/update",
        "userRemove": "api/users/remove",
    }

    def __init__(self):
        """
        Intialize configuration
        Creates the configuration folder and initialize or load configuraiton
        """
        self.http = Http(user_agent=self.user_agent)
        self._url: str = ""
        self._token: str = ""
        self._name: str = ""
        self._file_name = f"{self.config_dir}/{self.config_file}"
        if not os.path.isdir(self.config_dir):
            os.mkdir(self.config_dir)
        if not os.path.isfile(f"{self.config_dir}/{self.config_file}"):
            self.__save_config__()
        else:
            self.__load_config__()

    def get_token(self) -> str:
        """
        Return Bxt token
        :return:
        """
        return self._token

    def set_token(self, value: str):
        """
        Set Bxt token
        :param value:
        :return:
        """
        self._token = value
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

    def __str__(self):
        """
        Return textual representation of the configuration  class
        :return:
        """
        return f"BxtConfig(Url: '{self._url}', Name: '{self._name}', Token: '{self._token}')"

    def __save_config__(self):
        """
        Initialize configuration and write empty config
        :return:
        """
        config = {
            "token": self._token,
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
                self._token = data["token"]
            except (KeyError,) as e:
                self._token = ""

            try:
                self._name = data["name"]
            except (KeyError,) as e:
                self._name = ""

            try:
                self._url = f"{data['url']}"
            except (KeyError,) as e:
                self._url = ""
        except (FileNotFoundError,):
            self._token = ""
            self._name = ""
            self._url = ""
        except (Exception,):
            pass

    def configure(self) -> bool:
        """
        Create BctCtl configuration
        :return:
        """
        options = _get_user_input_for_config()
        passwd = pwinput(prompt="password: ", mask="")
        self._name = options["name"]
        self._url = options["url"]
        self._token = self.http.get_token(url=f"{self._url}/{self.endpoint['auth']}", name=self._name, passwd=passwd)
        self.__save_config__()
        if self._token == "":
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
        self._token = self.http.get_token(url=f"{self._url}/{self.endpoint['auth']}", name=username, passwd=password)
        self._name = username
        self.__save_config__()
        if self._token == "":
            return False
        return True

    def verify(self) -> bool:
        return self.http.verify_token(url=f"{self._url}/{self.endpoint['verify']}")


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
