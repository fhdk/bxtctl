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
import cmd2
from cmd2 import Cmd2ArgumentParser, with_argparser
import sys
from Bxt.Acl import Acl
from Bxt.Config import Config
from Bxt.Http import Http


class BxtCtl(cmd2.Cmd):
    """
    Main application object
    """
    config = Config()
    prompt = f"({config.get_name()}@bxt) $ "
    http = Http(Config.user_agent, config.get_token())
    sections = http.get_sections(f"{config.get_url()}/{Config.endpoint['sections']}")
    acl = Acl(sections)

    list_args = Cmd2ArgumentParser(description="List content of repo branch architecture")
    list_args.add_argument("repo", type=str, help="Target Repository", choices=acl.get_repositories())
    list_args.add_argument("branch", type=str, help="Target Branch", choices=acl.get_branches())
    list_args.add_argument("arch", type=str, help="Target Artitecture", choices=acl.get_architectures())

    comp_args = Cmd2ArgumentParser(description="Compare repo package across branches and architecures")
    comp_args.add_argument("repo", type=str, help="Target Repository", choices=acl.get_repositories())
    comp_args.add_argument("-b", "--branch", type=str, nargs="+", help="Branches", choices=acl.get_branches())
    comp_args.add_argument("-a", "--arch", type=str, nargs="+", help="Architecure", choices=acl.get_architectures())
    comp_args.add_argument("-p", "--package", type=str, nargs="+", help="Packages to compare")

    commit_args = Cmd2ArgumentParser(description="Commit package to repository")
    commit_args.add_argument("-p", "--package", type=str, help="Path to package file")
    commit_args.add_argument("-f", "--pkgfile", type=str, help="Path to package file")
    commit_args.add_argument("-s", "--sigfile", type=str, help="Path to signature file")
    commit_args.add_argument("repo", type=str, help="Target Repository", choices=acl.get_repositories())
    commit_args.add_argument("branch", type=str, help="Target Branch", choices=acl.get_branches())
    commit_args.add_argument("arch", type=str, help="Target Architecture", choices=acl.get_architectures())

    def __init__(self):
        super().__init__()

        # if config is uninitialized force setup config
        if self.config.get_url() == "" or self.config.get_name() == "":
            print("Enter initial configuration")
            if not self.config.configure():
                print("Initialization failed")
                exit(1)
            self.prompt = f"({self.config.get_name()}@bxt) $ "

        # if token is empty - login
        if self.config.get_token() == "":
            print("First time login")
            if not self.config.login():
                print("Login failed")
                exit(1)

        print(f"TODO - remove this block")
        print(f"---------- PERMISSIONS ---------- ")
        print(f"bxt user: '{self.config.get_name()}' has access to:")
        print(f"Branches      : {self.acl.get_branches()}")
        print(f"Architectures : {self.acl.get_architectures()}")
        print(f"Repositories  : {self.acl.get_repositories()}")
        print(f"--------------------------------- ")

    @with_argparser(list_args)
    def do_list(self, args):
        """
        List content of selected repo
        :param args:
        :return:
        """
        pkgs = self.http.get_packages(f"{self.config.get_url()}/{self.config.endpoint['packages']}", args.branch, args.repo, args.arch)
        for pkg in pkgs:
            print(f"{pkg['name']:<30}: {pkg['preferredCandidate']['version']}")

    @with_argparser(comp_args)
    def do_compare(self, args):
        """
        Compare branches
        :param args:
        :return:
        """
        branches = args.branch
        architectures = args.arch
        from pprint import pprint
        for branch in branches:
            for arch in architectures:
                archpkgs = self.http.get_packages(f"{self.config.get_url()}/{self.config.endpoint['packages']}", branch, args.repo, arch)
                pkgs = [x for x in archpkgs if x["name"] in args.package]
                for pkg in pkgs:
                    pprint(pkg)

    @with_argparser(commit_args)
    def do_commit(self, args):
        """
        Commpit package to repo
        :param args:
        :return: True/False
        """
        print("TODO - commit package to repo")
        pass

    def do_login(self):
        """
        Login
        :return: True/False
        """
        if not self.config.login():
            print("Login failed!")

    def do_configure(self):
        """
        Reconfigure
        :return: True/False
        """
        if not self.config.configure():
            print("Configuration failed!")


def start():
    """
    Poetry entry point
    :return:
    """
    app = BxtCtl()
    sys.exit(app.cmdloop())


if __name__ == '__main__':
    """
    Main entry point
    """
    start()