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

import json
import logging
import os
from pathlib import Path

# app supplied sources
from bxtctl.pwinput import pwinput
from .BxtSession import BxtSession
from .BxtToken import BxtToken
from .BxtEncoder import BxtEncoder


class BxtConfig:
    """
    Main Settings Class
    """

    license_url = "https://www.gnu.org/licenses/agpl.html"
    app_name = "bxtctl"
    app_version = "0.6alpha"
    config_dir = f"{Path.home()}/.config/{app_name}"
    config_file = "config.json"
    user_agent = f"{app_name}/{app_version}"
    repos = []
    logevents = ("commits", "syncs", "deploys")
    locations = ("automated", "overlay", "sync")
    commitevents = ("added", "deleted", "moved", "copied", "syncs")
    committypes = ("Add", "Remove", "Update", "Copy", "Move")

    endpoint = {
        "auth": "api/auth",
        "refresh": "api/auth/refresh",
        "revoke": "api/auth/revoke",
        "pkgLog": "api/logs",
        "pkgList": "api/packages",
        "pkgCommit": "api/packages/commit",
        "pkgSection": "api/sections",
        "pkgCompare": "api/compare",
        "userInfo": "api/userinfo",
    }


    def __init__(self):
        """
        Intialize configuration
        Creates the configuration folder and initialize or load configuraiton
        """
        self._configstore = f"{self.config_dir}/{self.config_file}"
        self._http = BxtSession(user_agent=self.user_agent)
        self._batch_size = 10
        self._url: str = ""
        self._username: str = ""
        self._token: BxtToken = BxtToken()
        self._token_renew_threshold = 300
        self._workspace = f"{Path.home()}/bxt-workspace"

        # create config dir if not existing
        if not os.path.isdir(self.config_dir):
            os.mkdir(self.config_dir)
        if not os.path.isdir(self._workspace):
            os.mkdir(self._workspace)
        # check configstore on disk
        if not os.path.isfile(f"{self.config_dir}/{self.config_file}"):
            # generrate empty default
            self.__save_config__()
        else:
            # load config
            self.__load_config__()


    def configure(self) -> bool:
        """
        Create BctCtl configuration
        :return:
        """
        # get options - username and service url
        options = self.__get_basic_config__()
        # get password from user
        password = pwinput(prompt="password: ", mask="")
        # assign returned option to the configuration
        self._username = options["name"]
        self._url = options["url"]
        # get response from service
        result = self._http.authenticate(
            url=f"{self._url}/{self.endpoint["auth"]}",
            username=self._username,
            password=password,
        )
        # handle result
        if result.status() == 200:
            # assign content from result to token
            self._token = BxtToken(result.content())
            # save configuration
            self.__save_config__()
            return True
        return False


    def get_access_token(self) -> str:
        """
        Return Bxt token
        :return:
        """
        expires_in = self._token.get_access_expiration()
        logging.debug(
            "Token expires in %s. Threshold is %s",
            expires_in,
            self._token_renew_threshold,
        )
        if expires_in < self._token_renew_threshold:
            if not self.renew_access_token():
                if not self.login():
                    return ""
        return self._token.get_access_token()


    def get_batch_size(self) -> int:
        """
        Return batch size
        :return:
        """
        return self._batch_size


    def get_workspace(self) -> str:
        """
        Return workspace path
        :return:
        """
        return self._workspace


    def get_hostname(self) -> str:
        """
        get hostname without protocol
        :return:
        """
        return self._url.split("//")[-1]


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
        result = self._http.authenticate(
            url=f"{self._url}/{self.endpoint["auth"]}",
            username=username,
            password=password,
        )
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


    def renew_access_token(self) -> bool:
        """
        Renew access token
        :return:
        """
        if not self._token.get_refresh_expired():
            refresh_token = self._token.get_refresh_token()
            result = self._http.use_refresh_token(
                url=f"{self._url}/{self.endpoint["refresh"]}",
                token=self._token.get_access_token(),
                refresh_token=refresh_token,
            )
            if result.status() == 200:
                self._token = BxtToken(result.content())
                self.__save_config__()
                return True

        return False


    def revoke_refresh_token(self) -> bool:
        """
        Revoke refresh token
        :return:
        """
        result = self._http.revoke_refresh_token(
            url=f"{self._url}/{self.endpoint["revoke"]}",
            token=self._token.get_refresh_token(),
        )
        if result.status() == 200:
            self._token = {}
            self.__save_config__()
            return True
        return False


    def save(self) -> None:
        """
        save config
        :return:
        """
        self.__save_config__()


    def set_batch_size(self, batch_size: int) -> None:
        """
        Set batch size
        :param batch_size:
        :return:
        """
        self._batch_size = batch_size
        self.__save_config__()


    def set_workspace(self, workspace: str) -> None:
        """
        Set workspace
        :param workspace:
        :return:
        """
        self._workspace = workspace
        self.__save_config__()


    def valid_config(self) -> bool:
        """
        Verify if config is valid
        :return:
        """
        return self._url != "" and self._username != ""


    def valid_refresh(self) -> bool:
        """
        Verify if refresh token is valid
        :return:
        """
        return self._token.get_refresh_expired()


    def valid_token(self) -> bool:
        """
        Verify if access token is valid
        :return:
        """
        return self._token.get_access_expired()


    def __str__(self):
        """
        Return textual representation of the configuration  class
        :return:
        """
        return (
            f"BxtConfig(Url: '{self._url}', Name: '{self._username}', "
            f"Token: '{self._token}', TokenRenew: '{self._token_renew_threshold}s', "
            f"Batch: '{self._batch_size}pkgs', Workspace: '{self._workspace}')"
        )


    def __load_config__(self):
        """
        Load BxtCtl configuration
        The function assumes the file exist
        :return:
        """
        try:
            with open(self._configstore, "r") as infile:
                config = json.load(infile)
            # read workdir
            try:
                self._workspace = config["workspace"]
            except KeyError:
                pass
            # read name
            try:
                self._username = config["username"]
            except KeyError:
                self._username = ""
            # read url
            try:
                self._url = f"{config["url"]}"
            except KeyError:
                self._url = ""
            # read token
            try:
                self._token = BxtToken(config["token"])
            except KeyError:
                self._token = BxtToken()
            # read batch size
            try:
                self._batch_size = config["batch_size"]
            except KeyError:
                self._batch_size = 10
            try:
                self._token_renew_threshold = config["token_threshold"]
            except KeyError:
                self._token_renew_threshold = 300

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
            "batch_size": self._batch_size,
            "token": self._token,
            "url": self._url,
            "username": self._username,
            "workspace": self._workspace,
            "token_threshold": self._token_renew_threshold,
        }
        with open(self._configstore, "w") as cfg_file:
            json.dump(temp, cfg_file, indent=2, cls=BxtEncoder)


    def __validate_owner__(self) -> bool:
        """
        validate if token belongs to name in config
        :return:
        """
        return self._token.validate_owner(self._username)


    @staticmethod
    def __get_basic_config__() -> dict:
        """
        get config options from user input
        :return:
        """
        options = {"name": "", "url": ""}
        while True:
            options["url"] = input(f"bxt service  : ").strip()
            options["name"] = input(f"bxt username : ").strip()
            if (options["url"] != ""
                and options["name"] != ""
                and options["url"].startswith("http")):
                return options
            else:
                if not options["url"].startswith("http"):
                    print("url must start with http or https")
