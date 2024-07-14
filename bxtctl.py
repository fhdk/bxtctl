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
import os
from Bxt.BxtAcl import BxtAcl
from Bxt.BxtConfig import BxtConfig
from Bxt.BxtSession import BxtSession


class BxtCtl(cmd2.Cmd):
    """
    Main application object
    """

    config = BxtConfig()
    if not config.valid_config():
        config.configure()

    if not config.get_access_token():
        z = config.login()

    if config.valid_token():
        if not config.renew_access_token():
            z = config.login()

    prompt = f"({config.get_name()}@{config.get_hostname()}) $ "
    # cmd2.Cmd.prompt = f"({config.get_name()}@{config.get_hostname()}) $ "
    http = BxtSession(BxtConfig.user_agent, config.get_access_token())
    sections = http.get_sections(
        f"{config.get_url()}/{BxtConfig.endpoint['pkgSection']}", None
    )

    acl = BxtAcl(sections)
    # set workspace command
    workspace = Cmd2ArgumentParser(description="Get or set workspace")
    workspace.add_argument("-w", "--workspace", type=str, help="Full path to workspace")
    # ###############################################################
    # list command
    list_args = Cmd2ArgumentParser(
        description="List content of repo branch architecture"
    )
    list_args.add_argument(
        "branch", type=str, help="Target Branch", choices=acl.get_branches()
    )
    list_args.add_argument(
        "repo", type=str, help="Target Repository", choices=acl.get_repositories()
    )
    list_args.add_argument(
        "arch", type=str, help="Target Artitecture", choices=acl.get_architectures()
    )
    # ###############################################################
    # compare command
    comp_args = Cmd2ArgumentParser(
        description="Compare repo package across branches and architectures"
    )
    comp_args.add_argument(
        "-b",
        "--branch",
        type=str,
        nargs="*",
        help="Branches to compare",
        choices=acl.get_branches(),
    )
    comp_args.add_argument(
        "-r",
        "--repo",
        type=str,
        nargs="*",
        help="Repositories to compare",
        choices=acl.get_repositories(),
    )
    comp_args.add_argument(
        "-a",
        "--arch",
        type=str,
        nargs="*",
        help="Architecures to compare",
        choices=acl.get_architectures(),
    )
    comp_args.add_argument(
        "-p",
        "--package",
        type=str,
        nargs="?",
        help="Package(s) to compare (multiple -p can be passed)",
    )
    # ###############################################################
    # commit command
    commit_args = Cmd2ArgumentParser(description="Commit package(s) to repository")
    commit_args.add_argument(
        "branch", type=str, nargs=1, help="Target Branch", choices=acl.get_branches()
    )
    commit_args.add_argument(
        "repo",
        type=str,
        nargs=1,
        help="Target Repository",
        choices=acl.get_repositories(),
    )
    commit_args.add_argument(
        "arch",
        type=str,
        nargs=1,
        help="Target Architecture",
        choices=acl.get_architectures(),
    )
    commit_args.add_argument(
        "package",
        type=str,
        nargs="?",
        help="package filename(s) (multiple files can be passed)",
    )

    def __init__(self):
        super().__init__()
        # if config is uninitialized force setup config
        if self.config.get_url() == "" or self.config.get_name() == "":
            print("Enter initial configuration")
            if not self.config.configure():
                print("Initialization failed")
                exit(1)

        # if token is empty - login
        if self.config.get_access_token() == "":
            print("First time login")
            if not self.config.login():
                print("Login failed")
                exit(1)

        self.prompt = f"({self.config.get_name()}@{self.config.get_hostname()}) $ "

        print(f"TODO - remove this block")
        print(f"---------- PERMISSIONS ---------- ")
        print(f"bxt user: '{self.config.get_name()}' has access to:")
        print(f"Branches      : {self.acl.get_branches()}")
        print(f"Architectures : {self.acl.get_architectures()}")
        print(f"Repositories  : {self.acl.get_repositories()}")
        print(f"--------------------------------- ")

    @with_argparser(workspace)
    def do_workspace(self, args):
        """
        Get or set workspace
        :param args:
        :return:
        """
        if not args.workspace:
            print(f"Current workspace is: {self.config.workspace}")
        else:
            self.config.workspace = args.workspace
            self.config.save()

    @with_argparser(list_args)
    def do_list(self, args):
        """
        List content of selected repo
        :param args:
        :return:
        """
        pkgs = self.http.get_packages(
            f"{self.config.get_url()}/{self.config.endpoint['packages']}",
            args.branch,
            args.repo,
            args.arch,
            self.config.get_access_token(),
        )
        for pkg in pkgs:
            print(
                f"{pkg['name']:<30}: {pkg['poolEntries'][pkg['preferredLocation']]['version']}"
            )
            print(pkg)

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
                archpkgs = self.http.get_packages(
                    f"{self.config.get_url()}/{self.config.endpoint['packages']}",
                    branch,
                    args.repo,
                    arch,
                    self.config.get_access_token(),
                )
                if args.package is not None:
                    pkgs = [x for x in archpkgs if x["name"] in args.package]
                    for pkg in pkgs:
                        pprint(pkg)
                else:
                    for pkg in archpkgs:
                        pprint(pkg)

    @with_argparser(commit_args)
    def do_commit(self, args):
        """
        Commpit package to repo
        :param args:
        :return: True/False
        """
        print(f"TODO - commit package to repo - using {args}")
        print(f"Reading files from workspace: {self.config.workspace}")
        print(f"Commit package(s) to: {args.branch}/{args.repo}/{args.arch}")
        for pkg in args.package:
            print(f"commit package: {pkg}")

    def do_login(self, args):
        """
        Login
        :return: True/False
        """
        if not self.config.login():
            print("Login failed!")

        self.prompt = f"({self.config.get_name()}@{self.config.get_hostname()}) $ "

    def do_configure(self, args):
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


if __name__ == "__main__":
    """
    Main entry point
    """
    start()
