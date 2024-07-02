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
import base64
import json
import os
from pwinput import pwinput
from pathlib import Path
from .Http import Http
from .BxtToken import BxtToken
from .BxtEncoder import BxtEncoder


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
        "refresh": "api/auth/refresh",
        "revoke": "api/auth/revoke",
        "logs": "api/logs/packages",
        "pkgList": "api/packages",
        "pkgCommit": "api/packages/commit",
        "pkgSection": "api/sections",
    }

    def __init__(self):
        """
        Intialize configuration
        Creates the configuration folder and initialize or load configuraiton
        """
        self._configstore = f"{self.config_dir}/{self.config_file}"
        self._http = Http(user_agent=self.user_agent)
        self._url: str = ""
        self._username: str = ""
        self._token: BxtToken = BxtToken()

        # create config dir if not existing
        if not os.path.isdir(self.config_dir):
            os.mkdir(self.config_dir)
        # check configstore on disk
        if not os.path.isfile(f"{self.config_dir}/{self.config_file}"):
            # generrate empty default
            self.__save_config__()
        else:
            # load config
            self.__load_config__()

    def get_hostname(self) -> str:
        """
        get hostname without protocol
        :return:
        """
        return self._url.split("//")[-1]

    def get_refresh_token(self) -> str:
        """
        Get Refresh Token
        :return:
        """
        return self._token.get_refresh_token()

    def get_access_token(self) -> str:
        """
        Return Bxt token
        :return:
        """
        return self._token.get_access_token()

    def get_name(self) -> str:
        """
        Return Bxt username
        :return:
        """
        return self._username

    def get_url(self) -> str:
        """
        Return Bxt endpoint url
        :return:
        """
        return self._url

    def is_valid(self):
        return self._url != "" and self._username != ""

    def configure(self) -> bool:
        """
        Create BctCtl configuration
        :return:
        """
        # get options - username and service url
        options = _get_user_input_for_config()
        # get password from user
        password = pwinput(prompt="password: ", mask="")
        # assign returned option to the configuration
        self._username = options["name"]
        self._url = options["url"]
        # get response from service
        result = self._http.authenticate(url=f"{self._url}/{self.endpoint['auth']}",
                                         username=self._username,
                                         password=password)
        # handle result
        if result.status() == 200:
            # assign content from result to token
            self._token = BxtToken(result.content())
            # save configuration
            self.__save_config__()
            return True
        return False

    def login(self) -> bool:
        """
        request login credentials to get a token
        :return:
        """
        # display current service
        print(f"login bxt service : {self.get_hostname()}")
        # username prompt
        username = input(f"bxt ({self._username}) : ").strip()
        if username == "":
            username = self._username
        # password prompt
        password = pwinput(prompt="password: ", mask="")
        # get reponse from service
        result = self._http.authenticate(url=f"{self._url}/{self.endpoint['auth']}", username=username,
                                         password=password)
        # handle result
        if result.status() == 200:
            # assign username - could have been changed
            self._username = username
            # assign the result to the token
            self._token = BxtToken(result.content())
            # save configuration
            self.__save_config__()
            return True
        # replace current token
        self._token = BxtToken()
        self.__save_config__()
        return False

    def revoke_access(self) -> bool:
        result = self._http.revoke_refresh_token(f"{self._url}/{self.endpoint['revoke_access']}")
        if result.status() == 200:
            self._token = {}
            self.__save_config__()
            return True
        return False

    def __str__(self):
        """
        Return textual representation of the configuration  class
        :return:
        """
        return f"BxtConfig(Url: '{self._url}', Name: '{self._username}', Token: '{self._token}')"

    def __load_config__(self):
        """
        Load BxtCtl configuration
        The function assumes the file exist
        :return:
        """
        try:
            with open(self._configstore, "r") as infile:
                config = json.load(infile)
            # read name
            try:
                self._username = config['username']
            except KeyError:
                self._username = ""
            # read url
            try:
                self._url = f"{config['url']}"
            except KeyError:
                self._url = ""
            # read token
            try:
                self._token = BxtToken(config['token'])
            except KeyError:
                self._token = BxtToken()

        except json.JSONDecodeError:
            self._username = ""
            self._url = ""
            self._token = BxtToken()
        except FileNotFoundError:
            self._token = BxtToken()
            self._username = ""
            self._url = ""
        except (Exception,):
            pass

    def __save_config__(self):
        """
        Initialize configuration and write config
        :return:
        """
        temp = {
            "url": self._url,
            "username": self._username,
            "token": self._token,
        }
        with open(self._configstore, "w") as outfile:
            json.dump(temp, outfile, cls=BxtEncoder)

    def __validate_owner__(self) -> bool:
        """
        validate if token belongs to name in config
        :return:
        """
        return self._token.validate_owner(self._username)


def _get_user_input_for_config() -> dict:
    """
    get config options from user input
    :return:
    """
    options = {"name": "", "url": ""}
    while True:
        options["url"] = input(f"bxt service : ").strip()
        options["name"] = input(f"bxt username : ").strip()
        if options["url"] != "" and options["name"] != "" and options["url"].startswith("http"):
            return options
