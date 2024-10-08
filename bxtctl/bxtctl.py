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

import argparse
from os import lseek
from random import choices

import cmd2
from cmd2 import Cmd2ArgumentParser, with_argparser, with_argument_list, with_category
import functools
import subprocess
import sys
import logging

# app supplied sources
from bxtctl.Bxt.BxtAcl import BxtAcl
from bxtctl.Bxt.BxtConfig import BxtConfig
from bxtctl.Bxt.BxtSession import BxtSession
from bxtctl.Bxt.Utils import path_completion, fix_path, encode_package_data
from bxtctl.Bxt.BxtWorkspace import BxtWorkspace


class BxtCtl(cmd2.Cmd):
    """
    Main bctctl shell instance
    """

    def __init__(self):
        # shortcuts = dict(cmd2.DEFAULT_SHORTCUTS)
        shortcuts = dict()
        shortcuts.update(
            {
                "exit": "quit",
                "?": "help",
                "ws": "workspace",
                "cmp": "compare",
                "cfg": "configure",
                "lsp": "list_path",
                "lsr": "list_repo",
                "lsw": "list_workspace",
                "upkg": "upload_pkg",
                "rpkg": "remove_pkg",
                # "cpp": "copy_pkg",
                # "mvp": "move_pkg",
            }
        )
        super().__init__(shortcuts=shortcuts)
        # To remove built-in commands entirely, delete
        # the "do_*" function from the cmd2.Cmd class
        del cmd2.Cmd.do_alias
        del cmd2.Cmd.do_edit
        del cmd2.Cmd.do_macro
        del cmd2.Cmd.do_run_pyscript
        del cmd2.Cmd.do_run_script
        del cmd2.Cmd.do_shell

        # if config is uninitialized force setup config
        if self.cfg.get_url() == "" or self.cfg.get_name() == "":
            self.poutput("Enter initial configuration")
            if not self.cfg.configure():
                self.perror("Initialization failed")
                exit(1)

        # if token is empty - login
        if self.cfg.get_access_token() == "":
            self.poutput("First time login")
            if not self.cfg.login():
                self.perror("Login failed")
                exit(1)

        self.prompt = f"({self.cfg.get_name()}@{self.cfg.get_hostname()}) $ "

    prompt = f"nn@bxt $ "
    cfg = BxtConfig()
    if not cfg.valid_config():
        cfg.configure()

    if not cfg.get_access_token():
        z = cfg.login()

    if cfg.valid_token():
        if not cfg.renew_access_token():
            z = cfg.login()

    # initialize logging as early as possible
    logging.basicConfig(
        level=logging.INFO,
        filename=f"{fix_path(cfg.config_dir)}/bxtctl.log",
        filemode="w",
    )
    # initialize the prompt based on configuration information
    prompt = f"({cfg.get_name()}@{cfg.get_hostname()}) $ "

    # initialize a session object
    bxt_session = BxtSession(cfg.user_agent)

    # read sections for the current user from the bxt service endpoint
    sections = bxt_session.get_sections(
        f"{cfg.get_url()}/{cfg.endpoint['pkgSection']}",
        cfg.get_access_token(),
    )

    # set up the access control
    acl = BxtAcl(sections)

    # create a path completion object and store in configuration
    cfg.repos = path_completion(
        acl.get_branches, acl.get_repositories, acl.get_architectures
    )
    # ensure workspace has been initialized
    ws = BxtWorkspace(cfg.get_workspace(), cfg.repos)
    if not ws.init_workspace():
        ws.init_workspace()

    # ###############################################################
    # standalone arguments
    bxt_cli_args = cmd2.Cmd2ArgumentParser("Execute action and return to prompt.")
    bxt_cli_args.add_argument(
        "-getws", action="store_true", help="Get active workspace"
    )
    bxt_cli_args.add_argument(
        "-setws", help="Set active workspace. The full path to the workspace"
    )
    bxt_cli_args.add_argument(
        "-commit",
        type=str,
        nargs="?",
        choices=["*"] + cfg.repos,
        help=f"Commit active workspace or specified repo",
    )
    # bxt_cli_args.add_argument("-l", "--log", action="count", default=None,
    #                           help="Repeat for more verbose logging")

    # ###############################################################
    # shell command line arguments
    # get or set workspace
    bxt_workspace_args = Cmd2ArgumentParser(description="Get or set workspace")
    bxt_workspace_args.add_argument(
        "-w", "--workspace", type=str, help="Full path to workspace"
    )

    # list folder content
    bxt_list_folder_args = Cmd2ArgumentParser(description="List path content")
    bxt_list_folder_args.add_argument(
        "-l", "--long", action="store_true", help="use long list"
    )
    bxt_list_folder_args.add_argument(
        "path", type=str, nargs="?", default=".", help="Path to list content"
    )

    # list workspace content
    bxt_list_workspace_args = Cmd2ArgumentParser(description="List workspace content")
    bxt_list_workspace_args.add_argument(
        "-l", "--long", action="store_true", help="use long list"
    )
    bxt_list_workspace_args.add_argument(
        "path", type=str, nargs="?", default=".", help="Path to list content", choices=cfg.repos
    )

    # ###############################################################
    # list repo content
    bxt_list_repo_args = Cmd2ArgumentParser(
        description="List content of remote bxt repository"
    )
    bxt_list_repo_args.add_argument(
        "location", type=str, help=f"List repo content", choices=cfg.repos
    )

    # ###############################################################
    # compare repo command
    bxt_compare_repo_args = Cmd2ArgumentParser(
        description="Compare repo package across branches and architectures"
    )
    bxt_compare_repo_args.add_argument(
        "-b", type=str, nargs="*", help=f"Compare branches", choices=cfg.repos
    )

    # ##############################################################
    # upload path
    bxt_upload_target = Cmd2ArgumentParser(
        description="Upload package(s) to bxt storage"
    )
    bxt_upload_target.add_argument(
        "repo", type=str, help="Upload to repo", choices=cfg.repos
    )
    bxt_upload_target.add_argument(
        "-p", "--pkg", type=str, nargs="+", help=f"Package(s) to upload to bxt"
    )

    # ###############################################################
    # remove command
    bxt_remove_args = Cmd2ArgumentParser(
        description="Remove package(s) from bxt storage"
    )
    bxt_remove_args.add_argument(
        "repo", type=str, help="Remove from repo", choices=cfg.repos
    )
    bxt_remove_args.add_argument(
        "-p", "--pkg", type=str, nargs="+", help=f"Packages to remove from bxt"
    )

    # # ###############################################################
    # # copy command
    # bxt_copy_args = Cmd2ArgumentParser(description="Copy package(s) inside bxt storage")
    # bxt_copy_args.add_argument(
    #     "-f", "--from", type=str, help="Copy from repo", choices=cfg.repos
    # )
    # bxt_copy_args.add_argument(
    #     "-t", "--to", type=str, help="Copy to repo", choices=cfg.repos
    # )
    # bxt_copy_args.add_argument(
    #     "-p", "--pkg", type=str, nargs="+", help=f"Package(s) to copy in bxt"
    # )
    #
    # # ###############################################################
    # # move command
    # bxt_move_args = Cmd2ArgumentParser(description="Move package(s) inside bxt storage")
    # bxt_move_args.add_argument(
    #     "-f", "--from", type=str, help="Move from repo", choices=cfg.repos
    # )
    # bxt_move_args.add_argument(
    #     "-t", "--to", type=str, help="Move to repo", choices=cfg.repos
    # )
    # bxt_move_args.add_argument(
    #     "-p", "--pkg", type=str, nargs="+", help=f"Packages to move in bxt"
    # )

    # # set logging verbosity
    # if bxt_cli_args.parse_args().verbose:
    #     logging.getLogger("bxtctl").setLevel(bxt_cli_args.parse_args().verbose)
    #     print("Logging level set to %s" % logging.getLevelName(logging.getLogger("bxtctl").getEffectiveLevel()))

    # ###############################################################
    # standalone -> return workspace and exit
    if bxt_cli_args.parse_args().getws:
        print(cfg.get_workspace())
        exit(0)
    # ###############################################################
    # set workspace and exit
    if bxt_cli_args.parse_args().setws:
        cfg.set_workspace(fix_path(bxt_cli_args.parse_args().setws))
        print(f"Workspace set to: {cfg.get_workspace()}")
        cfg.save()
        exit(0)
    # ###############################################################
    # commit workspace and exit
    if bxt_cli_args.parse_args().commit:
        to_commit = bxt_cli_args.parse_args().commit
        # ###############################################################
        # commit specific branch/repo/arch
        if to_commit != "*":
            print(f"checking '{to_commit}'", end="\r")
            packages = ws.get_packages(to_commit)
            if len(packages) > 0:
                print(f"Uploading repo: '{to_commit}'")
                for pkg in packages:
                    if pkg.signature is None:
                        print(
                            f"'{pkg.package.split('/')[-1]}' has no signature... skipping",
                            end="\n",
                        )
                        continue
                    packed = encode_package_data(pkg)
                    print(f"Sending package... {pkg.package.split('/')[-1]}")
                    result = bxt_session.commit(
                        url=f"{cfg.get_url()}/{cfg.endpoint['pkgCommit']}",
                        token=cfg.get_access_token(),
                        files=packed,
                    )
                    if result is None:
                        print("fatal error")
                        exit(1)
                    if result.status() != 200:
                        print(f"Error: {result.status()}. Message: {result.content()}")
                        exit(1)
                    else:
                        ws.pkg_remove(pkg)

            else:
                print(f"Nothing to do in '{to_commit}'")
        # ###############################################################
        # commit everything
        else:
            print("checking all repos", end="\r")
            for repo in cfg.repos:
                packages = ws.get_packages(repo)
                if len(packages) > 0:
                    print(f"Uploading repo: '{repo}'")
                    for pkg in packages:
                        if pkg.signature is None:
                            print(
                                f"'{pkg.package}' has no signature... skipping",
                                end="\n",
                            )
                            continue
                        packed = encode_package_data(pkg)
                        print(f"Sending package... {pkg.package.split('/')[-1]}", end="\r")
                        result = bxt_session.commit(
                            url=f"{cfg.get_url()}/{cfg.endpoint['pkgCommit']}",
                            token=cfg.get_access_token(),
                            files=packed,
                        )
                        if result is None:
                            print("fatal error")
                            exit(1)
                        if result.status() != 200:
                            print(f"Package: {pkg.package.split('/')[-1]}")
                            print(f"Error: {result.status()} Message: {result.content()}")
                            exit(1)
                        else:
                            ws.pkg_remove(pkg)

                else:
                    print(f"Nothing to do in '{repo}'")
        exit(0)


    @with_argparser(bxt_remove_args)
    def do_remove_pkg(self, args):
        """
        Remove one or more package(s) from bxt storage
        :param args: the package(s) to remove from the target repo
        """
        self.poutput("TODO: implement removal")
        if not args.path:
            self.pwarning("no repo specified")
        if not args.pkg:
            self.pwarning("no packages specified")
            return
        self.poutput(args.path)
        self.poutput(args.pkg)

    complete_delete_pkg = functools.partialmethod(
        cmd2.Cmd.delimiter_complete, match_against=cfg.repos, delimiter="/"
    )

    # @with_argparser(bxt_copy_args)
    # def do_copy_pkg(self, args):
    #     """
    #     Copy one or more package(s) within bxt storage
    #     :param args: the package(s) to copy from source to target
    #     """
    #     self.poutput("TODO: implement copy")
    #
    # complete_copy_pkg = functools.partialmethod(
    #     cmd2.Cmd.delimiter_complete, match_against=cfg.repos, delimiter="/"
    # )
    #
    # @with_argparser(bxt_move_args)
    # def do_move_pkg(self, args):
    #     """
    #     Move one or more package(s) in bxt storage
    #     :param args: the package(s) to move from source to target
    #     """
    #     self.poutput("TODO: implement move")
    #
    # complete_move_pkg = functools.partialmethod(
    #     cmd2.Cmd.delimiter_complete, match_against=cfg.repos, delimiter="/"
    # )

    @with_argparser(bxt_workspace_args)
    def do_workspace(self, args):
        """
        Get or set workspace
        :param args: optional path to new workspace
        """
        if not args.workspace:
            self.poutput(f"Current workspace is: {self.cfg.get_workspace()}")
        else:
            ws_path = fix_path(args.workspace)
            ws = BxtWorkspace(ws_path, self.cfg.repos)
            if ws.init_workspace():
                self.poutput(f"Workspace {ws_path} created")
                self.cfg.set_workspace(ws_path)
                self.cfg.save()
            else:
                self.perror(f"No permission on workspace: {ws_path}")

    @with_argparser(bxt_list_workspace_args)
    def do_list_workspace(self, args):
        """
        List content of current workspace
        """
        path = args.path.strip("/")
        self.poutput(f"{self.cfg.get_workspace()}/{path}")
        cmd = ["ls"]
        if args.long:
            cmd.insert(len(cmd) + 1, "-l")
        cmd.insert(len(cmd) + 1, f"{self.cfg.get_workspace()}/{path}")
        subprocess.run(cmd)

    complete_list_workspcae = functools.partialmethod(
        cmd2.Cmd.delimiter_complete, match_against=cfg.repos, delimiter="/"
    )

    @with_argparser(bxt_list_folder_args)
    def do_list_path(self, args):
        """
        List content of specified folder
        :param args: full path to folder
        """
        cmd = ["ls"]
        if args.long:
            cmd.insert(len(cmd) + 1, "-l")
        cmd.insert(len(cmd) + 1, args.path)
        subprocess.run(cmd)

    @with_argparser(bxt_list_repo_args)
    def do_list_repo(self, args):
        """
        List content of selected repo
        :param args: path to repo e.g. branch/repo/arch
        """
        location = args.location.split("/")
        pkgs = self.bxt_session.get_packages(
            f"{self.cfg.get_url()}/{self.cfg.endpoint['pkgList']}",
            location[0],
            location[1],
            location[2],
            self.cfg.get_access_token(),
        )
        page_packages = ""
        count = 0
        for pkg in pkgs:
            self.poutput(f"Reading... {count + 1}", end="\r")
            page_packages = page_packages + f"{pkg['name']:<30}: {pkg['poolEntries'][pkg['preferredLocation']]['version']}\n"

        self.ppaged(page_packages, chop=True)
        # self.poutput(
        #     f"{pkg['name']:<30}: {pkg['poolEntries'][pkg['preferredLocation']]['version']}"
        # )

    complete_list_repo = functools.partialmethod(
        cmd2.Cmd.delimiter_complete, match_against=cfg.repos, delimiter="/"
    )

    @with_argparser(bxt_compare_repo_args)
    def do_compare(self, args):
        """
        Compare branches
        :param args:
        :return:
        """
        compare_us = []
        for location in args.location:
            element = location.strip("/").split("/")
            branch = element[0]
            if branch not in self.acl.get_branches():
                self.perror(f"No permissions: {branch} in {location}")
                return False
            repository = element[1]
            if repository not in self.acl.get_repositories():
                self.perror(f"No permissions: {repository} in {location}")
                return False
            architecture = element[2]
            if architecture not in self.acl.get_architectures():
                self.perror(f"No permissions: {architecture} in {location}")
                return False
            compare_us.append(
                {
                    "branch": branch,
                    "repository": repository,
                    "architecture": architecture,
                }
            )

        # send request
        compare_us = sorted(compare_us, key=lambda x: x["repository"])
        result = self.bxt_session.compare(
            url=f"{self.cfg.get_url()}/{self.cfg.endpoint["pkgCompare"]}",
            data=compare_us,
            token=self.cfg.get_access_token(),
        )
        print(result)
        compare_table = result.content()["compareTable"]
        pkgname_len = max(len(elm) for elm in compare_table) + 1

        pkg_list = []
        table_headers = []
        for target in compare_us:
            content = (
                f"{target['branch']}/{target['repository']}/{target['architecture']}"
            )
            table_headers.append(content)

        table_header_len = max(len(elm) for elm in table_headers) + 1
        compare_header = f"{"Packages":<{pkgname_len}}"
        for table_header in table_headers:
            compare_header += f"{table_header:>{table_header_len}}"

        for k, package in enumerate(compare_table.items()):
            pkg = {"name": package[0], "versions": []}
            pkg_versions = package[1]
            for key in pkg_versions.keys():
                # TODO implement the available locations
                # TODO: names describing where the version is placed
                # TODO: stored in config.locations

                if package[1][key] not in pkg["versions"]:
                    try:
                        pkg["versions"].append(
                            {"location": key, "version": package[1][key]["overlay"]}
                        )
                    except KeyError:
                        pkg["versions"].append(
                            {"location": key, "version": package[1][key]["automated"]}
                        )
            missing = [x for x in table_headers if x not in pkg_versions.keys()]
            for m in missing:
                pkg["versions"].append({"location": m, "version": "-"})
            # sort the version list for presentation
            pkg["versions"] = list(sorted(pkg["versions"], key=lambda x: x["location"]))
            pkg_list.append(pkg)

        pkg_list = sorted(pkg_list, key=lambda x: x["name"])
        # ------------ print result to screen -------------------------
        print(compare_header)
        print("-" * len(compare_header))

        for pkg in pkg_list:
            pkg_name = pkg["name"]
            pkg_versions = pkg["versions"]
            print(f"{pkg_name:<{pkgname_len}}", end="")
            for table_header in table_headers:
                version = next(
                    (
                        v["version"]
                        for v in pkg_versions
                        if v["location"] == table_header
                    ),
                    "-",
                )
                print(f"{version:>{table_header_len}}", end="")
            print()

    complate_compare_repo = functools.partialmethod(
        cmd2.Cmd.delimiter_complete, match_against=cfg.repos, delimiter="/"
    )

    @with_argparser(bxt_upload_target)
    def do_upload_pkg(self, args):
        """
        Commpit package(s) to repo
        :param args:
        :return: True/False
        """
        # location = args.path.split("/")
        # branch = location[0]
        # if branch not in self.acl.get_branches():
        #     self.perror(f"Invalid branch: {branch}")
        #     return False
        # repo = location[1]
        # if repo not in self.acl.get_repositories():
        #     self.perror(f"Invalid repository: {repo}")
        #     return False
        # arch = location[2]
        # if arch not in self.acl.get_architectures():
        #     self.perror(f"Invalid architecture: {arch}")
        #     return False
        # packages = args.package
        self.quiet = False
        # self.pfeedback(f"TODO - commit package to repo - using {packages}")
        self.pfeedback(f"Reading files from workspace: {self.cfg.get_workspace()}/{args.repo}")
        self.pfeedback(f"Commit endpoint is: {self.cfg.endpoint['pkgCommit']}")
        self.pfeedback(f"Commit to repo: {args.repo}")
        self.pfeedback(f"Commit package(s): {args.pkg}")
        # self.quiet = True
        # ws = BxtWorkspace(self.cfg.get_workspace(), self.cfg.repos)
        # packages = ws.get_packages(repo)
        # to_send = args.pkg
        #
        # if len(packages) > 0:
        #     print(f"Uploading repo: '{repo}'")
        #     for pkg in packages:
        #         if pkg.signature is None:
        #             print(
        #                 f"'{pkg.package()}' has no signature... skipping",
        #                 end="\n",
        #             )
        #             continue
        #         packed = encode_package_data(pkg)
        #         print(f"Sending package... {pkg.package.split('/')[-1]}")
        #         result = self.bxt_session.commit(
        #             url=f"{self.cfg.get_url()}/{self.cfg.endpoint['pkgCommit']}",
        #             token=self.cfg.get_access_token(),
        #             files=packed,
        #         )
        #         if result.status() != 200:
        #             print(f"Error: {result.status()}. Message: {result.content()}")
        #             exit(1)
        #         else:
        #             ws.pkg_remove(pkg)
        # print("Files has been sent.")

    complete_upload = functools.partialmethod(
        cmd2.Cmd.delimiter_complete, match_against=cfg.repos, delimiter="/"
    )

    def do_login(self, args):
        """
        Retrieve JWT credentials for the configured bxt service
        """
        if not self.cfg.login():
            self.perror("Login failed!")
        # update prompt
        self.prompt = f"({self.cfg.get_name()}@{self.cfg.get_hostname()}) $ "

    def do_configure(self, args):
        """
        Configure endpoint and credentials
        """
        if not self.cfg.configure():
            self.perror("Configuration failed!")
        # update prompt
        self.prompt = f"({self.cfg.get_name()}@{self.cfg.get_hostname()}) $ "

    def do_permissions(self, args):
        """ "
        List permissions
        """
        self.pwarning(f"---------- PERMISSIONS ---------- ")
        self.poutput(f"bxt user      : {self.cfg.get_name()}")
        self.poutput(f"Branches      : {str.join(", ", self.acl.get_branches())}")
        self.poutput(f"Repositories  : {str.join(", ", self.acl.get_repositories())}")
        self.poutput(f"Architectures : {str.join(", ", self.acl.get_architectures())}")
        self.poutput(f"--------------------------------- ")


    def start_bxtctl(self):
        """
        Poetry entry point
        :return:
        """
        if sys.platform.startswith("win"):
            print(f"unsupported operating system: {sys.platform}")
            exit(255)
        app = self
        sys.exit(app.cmdloop())


def start():
    """
    poetry entry point
    :return:
    """
    app = BxtCtl()
    app.start_bxtctl()


if __name__ == "__main__":
    """
    Main entry point
    """
    start()
