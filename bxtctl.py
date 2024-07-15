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
import subprocess
import sys
import os
from Bxt.BxtAcl import BxtAcl
from Bxt.BxtConfig import BxtConfig
from Bxt.BxtSession import BxtSession


def do_ls(args):
    """
    List content of workspace
    :param args:
    :return:
    """
    subprocess.run(["bxt", "ls", args.workspace])


class BxtCtl(cmd2.Cmd):
    """
    Main bctctl shell instance
    """
    def __init__(self):
        # shortcuts = dict(cmd2.DEFAULT_SHORTCUTS)
        shortcuts = dict()
        shortcuts.update({
            "?": "help",
            "!": "shell",
            "cp": "bxtcopy",
            "exit": "quit",
            "lsp": "ls_path",
            "lsr": "ls_repo",
            "lsw": "ls_workspace",
            "mv": "move",
            "rm": "remove",
            "up": "commit",
            "upload": "commit",
            "ws": "workspace"
        })
        super().__init__(shortcuts=shortcuts)
        # To remove built-in commands entirely, delete
        # the "do_*" function from the cmd2.Cmd class
        del cmd2.Cmd.do_alias
        del cmd2.Cmd.do_edit
        del cmd2.Cmd.do_macro
        del cmd2.Cmd.do_run_pyscript
        del cmd2.Cmd.do_run_script
        # if config is uninitialized force setup config
        if self.config.get_url() == "" or self.config.get_name() == "":
            self.poutput("Enter initial configuration")
            if not self.config.configure():
                self.perror("Initialization failed")
                exit(1)

        # if token is empty - login
        if self.config.get_access_token() == "":
            self.poutput("First time login")
            if not self.config.login():
                self.perror("Login failed")
                exit(1)

        self.prompt = f"({self.config.get_name()}@{self.config.get_hostname()}) $ "

        self.pwarning(f"TODO - remove this block")
        self.pwarning(f"---------- PERMISSIONS ---------- ")
        self.pwarning(f"bxt user: '{self.config.get_name()}' has access to:")
        self.pwarning(f"Branches      : {self.acl.get_branches()}")
        self.pwarning(f"Repositories  : {self.acl.get_repositories()}")
        self.pwarning(f"Architectures : {self.acl.get_architectures()}")
        self.pwarning(f"--------------------------------- ")

    prompt = f"nn@bxt $ "
    config = BxtConfig()
    if not config.valid_config():
        config.configure()

    if not config.get_access_token():
        z = config.login()

    if config.valid_token():
        if not config.renew_access_token():
            z = config.login()

    prompt = f"({config.get_name()}@{config.get_hostname()}) $ "
    # initialize a session object
    bxt_session = BxtSession(BxtConfig.user_agent)
    sections = bxt_session.get_sections(
        f"{config.get_url()}/{BxtConfig.endpoint['pkgSection']}",
        config.get_access_token(),
    )

    acl = BxtAcl(sections)
    # ###############################################################
    # list workspace content
    list_workspace_args = Cmd2ArgumentParser(description="List workspace content")
    list_workspace_args.add_argument(
        "-l", "--long", action="store_true", help="use long list"
    )

    # ###############################################################
    # list folder content
    list_folder_args = Cmd2ArgumentParser(description="List path content")
    list_folder_args.add_argument(
        "-l", "--long", action="store_true", help="use long list"
    )
    list_folder_args.add_argument(
        "path", type=str, nargs="?", default=".", help="Path to list content"
    )

    # ###############################################################
    # set workspace command
    workspace_args = Cmd2ArgumentParser(description="Get or set workspace")
    workspace_args.add_argument(
        "-w", "--workspace", type=str, help="Full path to workspace"
    )

    # ###############################################################
    # list repo command
    list_repo_args = Cmd2ArgumentParser(
        description="List content of remote bxt repository"
    )
    list_repo_args.add_argument(
        "location",
        type=str,
        help=f"{acl.get_branches()}/{acl.get_repositories()}/{acl.get_architectures()}",
    )
    # ###############################################################
    # compare command
    compare_args = Cmd2ArgumentParser(
        description="Compare repo package across branches and architectures"
    )
    compare_args.add_argument(
        "-l",
        "--location",
        type=str,
        nargs="*",
        help=f"{acl.get_branches()}/{acl.get_repositories()}/{acl.get_architectures()}",
    )
    compare_args.add_argument(
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
        "location",
        type=str,
        help=f"{acl.get_branches()}/{acl.get_repositories()}/{acl.get_architectures()}",
    )
    commit_args.add_argument(
        "-p",
        "--package",
        type=str,
        nargs="+",
        help="package name(s) (multiple files can be passed)",
    )

    # ###############################################################
    # copy command
    bxt_copy_args = Cmd2ArgumentParser(description="Copy package(s) inside bxt storage")
    bxt_copy_args.add_argument(
        "-p",
        "--package",
        type=str,
        nargs="+",
        help=f"'pkgname {acl.get_branches()}/{acl.get_repositories()}/{acl.get_architectures()} {acl.get_branches()}/{acl.get_repositories()}/{acl.get_architectures()}'",
    )

    # ###############################################################
    # move command
    bxt_move_args = Cmd2ArgumentParser(description="Move package(s) inside bxt storage")
    bxt_move_args.add_argument(
        "-p",
        "--package",
        type=str,
        nargs="+",
        help=f"Package move from repo to repo: 'pkgname {acl.get_branches()}/{acl.get_repositories()}/{acl.get_architectures()} {acl.get_branches()}/{acl.get_repositories()}/{acl.get_architectures()}'",
    )

    # ###############################################################
    # remove command
    bxt_delete_args = Cmd2ArgumentParser(
        description="Delete package(s) inside bxt storage"
    )
    bxt_delete_args.add_argument(
        "-p",
        "--package",
        type=str,
        nargs="+",
        help=f"Package remove from repo: 'pkgname {acl.get_branches()}/{acl.get_repositories()}/{acl.get_architectures()}'",
    )

    @with_argparser(bxt_delete_args)
    def do_remove(self, args):
        """
        Remove one or more package(s) from bxt storage
        :param args: the package(s) to remove from the target repo
        """
        self.poutput("TODO: implement removal")

    @with_argparser(bxt_copy_args)
    def do_copy(self, args):
        """
        Copy one or more package(s) within bxt storage
        :param args: the package(s) to copy from source to target
        """
        self.poutput("TODO: implement copy")

    @with_argparser(bxt_move_args)
    def do_move(self, args):
        """
        Move one or more package(s) in bxt storage
        :param args: the package(s) to move from source to target
        """
        self.poutput("TODO: implement move")

    @with_argparser(workspace_args)
    def do_workspace(self, args):
        """
        Get or set workspace
        :param args: optional path to new workspace
        """
        if not args.workspace:
            self.poutput(f"Current workspace is: {self.config.workspace}")
        else:
            self.config.workspace = args.workspace
            self.config.save()

    @with_argparser(list_workspace_args)
    def do_ls_workspace(self, args):
        """
        List content of current workspace
        """
        self.poutput("Current workspace is: " + self.config.workspace)
        cmd = ["ls"]
        if args.long:
            cmd.insert(len(cmd) + 1, "-l")
        cmd.insert(len(cmd) + 1, self.config.workspace)
        subprocess.run(cmd)

    @with_argparser(list_folder_args)
    def do_ls_path(self, args):
        """
        List content of specified folder
        :param args: full path to folder
        """
        cmd = ["ls"]
        if args.long:
            cmd.insert(len(cmd) + 1, "-l")
        cmd.insert(len(cmd) + 1, args.path)
        subprocess.run(cmd)

    @with_argparser(list_repo_args)
    def do_ls_repo(self, args):
        """
        List content of selected repo
        :param args: path to repo e.g. branch/repo/arch
        """
        location = args.location.split("/")
        pkgs = self.bxt_session.get_packages(
            f"{self.config.get_url()}/{self.config.endpoint['pkgList']}",
            location[0],
            location[1],
            location[2],
            self.config.get_access_token(),
        )
        for pkg in pkgs:
            self.poutput(
                f"{pkg['name']:<30}: {pkg['poolEntries'][pkg['preferredLocation']]['version']}"
            )

    @with_argparser(compare_args)
    def do_compare(self, args):
        """
        Compare branches
        :param args:
        :return:
        """
        locations = args.location
        print(locations)
        # branches = args.branch
        # architectures = args.arch
        #
        # for branch in branches:
        #     for arch in architectures:
        #         archpkgs = self.bxt_session.get_packages(
        #             f"{self.config.get_url()}/{self.config.endpoint['pkgCompare']}",
        #             args.branch,
        #             args.repo,
        #             arch,
        #             self.config.get_access_token(),
        #         )
        #         if args.package is not None:
        #             pkgs = [x for x in archpkgs if x["name"] in args.package]
        #             for pkg in pkgs:
        #                 self.poutput(pkg)
        #         else:
        #             for pkg in archpkgs:
        #                 self.poutput(pkg)

    @with_argparser(commit_args)
    def do_commit(self, args):
        """
        Commpit package(s) to repo
        :param args:
        :return: True/False
        """
        location = args.location.strip("/").split("/")
        branch = location[0]
        if branch not in self.acl.get_branches():
            self.perror(f"Invalid branch: {branch}")
            return False
        repo = location[1]
        if repo not in self.acl.get_repositories():
            self.perror(f"Invalid repository: {repo}")
            return False
        arch = location[2]
        if arch not in self.acl.get_architectures():
            self.perror(f"Invalid architecture: {arch}")
            return False
        packages = args.package
        self.quiet = False
        self.pfeedback(f"TODO - commit package to repo - using {packages}")
        self.pfeedback(f"Reading files from workspace: {self.config.workspace}")
        self.pfeedback(f"Commit endpoint is: {self.config.endpoint['pkgCommit']}")
        self.pfeedback(f"Commit package(s) to: {branch}/{repo}/{arch}")
        for pkg in packages:
            self.pfeedback(f"commit package: {pkg}")
        self.quiet = True

    def do_login(self, args):
        """
        Retrieve JWT credentials for the configured bxt service
        """
        if not self.config.login():
            self.perror("Login failed!")

        self.prompt = f"({self.config.get_name()}@{self.config.get_hostname()}) $ "

    def do_configure(self, args):
        """
        Configure endpoint and credentials
        """
        if not self.config.configure():
            self.perror("Configuration failed!")


def start():
    """
    Poetry entry point
    :return:
    """
    if sys.platform.startswith("win"):
        print(f"unsupported operating system: {sys.platform}")
        exit(255)
    app = BxtCtl()
    sys.exit(app.cmdloop())


if __name__ == "__main__":
    """
    Main entry point
    """
    start()
