#!/usr/bin/env python3
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

import argparse
import json
import os
import requests
from pwinput import pwinput
from cmd import Cmd
from pathlib import Path

license_url = "https://www.gnu.org/licenses/agpl.html"
app_name = "bxtctl"
version = "0.1.0"
user_agent = F"{app_name}/{version}"
config_dir = f"{Path.home()}/.config/{app_name}"
config_file = f"config.json"
bxt_commands = ["commit", "compare", "configure", "login", "ls", "shell"]
endpoint = {
    "auth": "api/auth",
    "sections": "api/sections/get",
    "packages": "api/packages/get",
    "commit": "api/packages/commit",
    "logs": "api/logs/packages",
    "verify": "api/verify",
}


class Packages:
    def __init__(self):
        pass


class BxtSettings:
    def __init__(self, folder: str, file_name: str):
        self._url: str = ""
        self._token: str = ""
        self._name: str = ""
        self._file_name = f"{folder}/{file_name}"
        if not os.path.exists(folder):
            os.mkdir(folder)
        if not os.path.isfile(f"{folder}/{file_name}"):
            self._save_config()
        else:
            self._load_config()

    def get_token(self) -> str:
        return self._token

    def set_token(self, value: str):
        self._token = value

    def get_name(self) -> str:
        return self._name

    def set_name(self, value: str):
        self._name = value

    def get_url(self) -> str:
        return self._url

    def set_url(self, value: str):
        self._url = value

    def __str__(self):
        return f"BxtConfig(Url: '{self._url}', Name: '{self._name}', Token: '{self._token}')"

    def _save_config(self):
        config = {
            "token": self._token,
            "name": self._name,
            "url": self._url
        }
        with open(self._file_name, "w") as outfile:
            json.dump(config, outfile)

    def _load_config(self):
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
        options = _get_config_options()
        passwd = pwinput(prompt="password: ", mask="")
        self._name = options["name"]
        self._url = options["url"]
        self._token = _http_get_token(url=f"{self._url}/{endpoint['auth']}", name=self._name, passwd=passwd)
        self._save_config()
        if self._token == "":
            return False
        return True

    def login(self) -> bool:
        username = input(f"bxt user ({self._name}): ").strip()
        if username == "":
            username = self._name
        password = pwinput(prompt="password: ", mask="")
        self._token = _http_get_token(url=f"{self._url}/{endpoint['auth']}", name=username, passwd=password)
        self._save_config()
        if self._token == "":
            return False
        return True


class Shell(Cmd):
    prompt = f"({app_name}) > "

    @staticmethod
    def do_exit(cmd: str) -> bool:
        return True

    @staticmethod
    def help_exit():
        print("To exit BxtCmd use 'exit()'. Shorthand 'x', 'q' or Ctrl-D.")

    def default(self, cmd: str):
        if cmd == 'x' or cmd == 'q':
            return self.do_exit(cmd)

        print("Default: {}".format(cmd))

    do_EOF = do_exit
    help_EOF = help_exit


class BxtAcl:
    def __init__(self, sections: list):
        self._sections = sections

    def get_sections(self):
        return self._sections

    def get_architectures(self) -> set:
        architectures = []
        for section in self._sections:
            architectures.append(section["architecture"])
        return set(architectures)

    def get_branches(self):
        if not self._sections:
            return set()
        branches = []
        for section in self._sections:
            branches.append(section["branch"])
        return set(branches)

    def get_repositories(self):
        if not self._sections:
            return set()
        repositories = []
        for section in self._sections:
            repositories.append(section["repository"])
        return set(repositories)


def _http_get_acl(url: str, token: str) -> list:
    try:
        session = _build_session(token)
        session = session.get(url)
        return json.loads(session.text)

    except (requests.exceptions.ConnectionError,) as err:
        print(f"{err}")

    return []


def _get_config_options() -> dict:
    options = {"name": "", "url": ""}
    while True:
        options["url"] = input(f"bxt http: ").strip()
        options["name"] = input(f"bxt user: ").strip()
        if options["url"] and options["name"] != "":
            return options


def _http_verify_token(url: str, token: str) -> bool:
    try:
        session = _build_session(token)
        session = session.get(url)
        if session.status_code == 200:
            return True

    except (Exception,) as e:
        print(e)

    return False


def _http_get_token(url: str, name: str, passwd: str) -> str:
    credentials = {"name": name, "password": passwd}
    try:
        session = _build_session()
        session = session.post(url, json=credentials)
        print(session)
        if session.status_code == 200:
            cookie_jar = requests.utils.dict_from_cookiejar(session.cookies)
            try:
                token = cookie_jar["token"]
                print(token)
                return token
            except (KeyError,):
                print("CookieJar is empty :(")
    except (Exception,) as err:
        print(err)
    return ""


def _build_session(token: str = None) -> requests.session():
    session = requests.session()
    session.headers.update({"User-Agent": user_agent})
    if token is not None:
        session.cookies.update({"token": token})
    return session


class BxtCtl:
    def __init__(self):
        pass

    @staticmethod
    def run():
        config = BxtSettings(config_dir, config_file)
        # if config is uninitialized force setup config
        if config.get_url() == "" or config.get_name() == "":
            if not config.configure():
                print("Initialization failed")
                exit(1)

        if config.get_token() == "":
            if not config.login():
                print("Login failed")
                exit(1)

        sections = _http_get_acl(f"{config.get_url()}/{endpoint['sections']}", config.get_token())
        acl = BxtAcl(sections)
        print(f"bxt user: '{config.get_name()}' has access to:")
        print(f"Branches      : {acl.get_branches()}")
        print(f"Architectures : {acl.get_architectures()}")
        print(f"Repositories  : {acl.get_repositories()}")

        parser = argparse.ArgumentParser(
            prog=f"{app_name}",
            description="Command line tool for bxt package management.",
            epilog=f"{app_name} v.{version} - AGPL v3 or later <{license_url}>")
        parser.add_argument("command",
                            type=str,
                            help="Command to execute",
                            choices=bxt_commands)
        parser.add_argument("-b", "--branch", type=str, choices=acl.get_branches(), help="Target Branch")
        parser.add_argument("-r", "--repo", type=str, choices=acl.get_repositories(), help="Target Repository")
        parser.add_argument("-a", "--archictecre", type=str, choices=acl.get_architectures(), help="Target Architecture")
        parser.add_argument("-p", "--package", type=str, nargs="+", help="Target Package")
        args = parser.parse_args()

        if args.command == "reconfigure":
            if not config.configure():
                print("Reconfiguration failed.")
                exit(1)

        if args.command == "commit":

            print("TODO - commit package to branch/repo/arch")
            exit(0)

        if args.commmand == "compare":
            print("TODO - compare two packges in /repo/arch")
            exit(0)

        if args.command == "ls":
            print("TODO - list packages from branch/repo/arch")
            exit(0)

        if args.command == "login":
            config.login()
            exit(0)

        if args.command == "shell":
            Shell().cmdloop()
            exit(0)


def start():
    app = BxtCtl()
    app.run()


if __name__ == '__main__':
    start()
