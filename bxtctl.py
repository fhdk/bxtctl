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
import logging
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder
from Bxt.BxtAcl import BxtAcl
from Bxt.BxtConfig import BxtConfig
from Bxt.BxtSession import BxtSession
from Bxt.Utils import path_completion, fix_path, encode_package_data
from Bxt.BxtWorkspace import BxtWorkspace

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
                "cmp": "compare",
                "cpp": "copy_pkg",
                "cfg": "configure",
                "mvp": "move_pkg",
                "lsp": "list_path",
                "lsr": "list_repo",
                "lsw": "list_workspace",
                "rmp": "delete_pkg",
                "upp": "upload",
                "ws": "workspace",
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
    bxt_session = BxtSession(config.user_agent)
    sections = bxt_session.get_sections(
        f"{config.get_url()}/{config.endpoint['pkgSection']}",
        config.get_access_token(),
    )

    acl = BxtAcl(sections)
    config.repos = path_completion(acl.get_branches, acl.get_repositories, acl.get_architectures)

    # ###############################################################
    # list workspace content
    bxt_list_workspace_args = Cmd2ArgumentParser(description="List workspace content")
    bxt_list_workspace_args.add_argument(
        "-l", "--long", action="store_true", help="use long list"
    )

    # ###############################################################
    # list folder content
    bxt_list_folder_args = Cmd2ArgumentParser(description="List path content")
    bxt_list_folder_args.add_argument(
        "-l", "--long", action="store_true", help="use long list"
    )
    bxt_list_folder_args.add_argument(
        "path", type=str, nargs="?", default=".", help="Path to list content"
    )

    # ###############################################################
    # set workspace command
    bxt_workspace_args = Cmd2ArgumentParser(description="Get or set workspace")
    bxt_workspace_args.add_argument(
        "-w", "--workspace", type=str, help="Full path to workspace"
    )

    # ###############################################################
    # list repo command
    bxt_list_repo_args = Cmd2ArgumentParser(
        description="List content of remote bxt repository"
    )
    bxt_list_repo_args.add_argument(
        "location",
        type=str,
        help=f"{acl.get_branches()}/{acl.get_repositories()}/{acl.get_architectures()}",
    )
    # ###############################################################
    # compare command
    bxt_compare_repo_args = Cmd2ArgumentParser(
        description="Compare repo package across branches and architectures"
    )
    bxt_compare_repo_args.add_argument(
        "-l",
        "--location",
        type=str,
        nargs="*",
        help=f"{acl.get_branches()}/{acl.get_repositories()}/{acl.get_architectures()}",
    )
    bxt_compare_repo_args.add_argument(
        "-p",
        "--package",
        type=str,
        nargs="?",
        help="Package(s) to compare (multiple -p can be passed)",
    )

    # ###############################################################
    # commit command
    bxt_upload_args = Cmd2ArgumentParser(description="Upload package(s) to repository")
    bxt_upload_args.add_argument(
        "-t", "--target",
        type=str,
        nargs="+",
        help=f"{acl.get_branches()}/{acl.get_repositories()}/{acl.get_architectures()}. Packages in active workspace will be uploaded.",
    )
    # commit_args.add_argument(
    #     "-p",
    #     "--package",
    #     type=str,
    #     nargs="+",
    #     help="package name(s) (multiple files can be passed)",
    # )

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
    def do_delete_pkg(self, args):
        """
        Remove one or more package(s) from bxt storage
        :param args: the package(s) to remove from the target repo
        """
        self.poutput("TODO: implement removal")

    # complete_delete_pkg = functools.partialmethod(cmd2.Cmd.delimiter_complete,
    #                                               match_against=config.paths,
    #                                               delimiter='/')

    @with_argparser(bxt_copy_args)
    def do_copy_pkg(self, args):
        """
        Copy one or more package(s) within bxt storage
        :param args: the package(s) to copy from source to target
        """
        self.poutput("TODO: implement copy")

    # complete_copy_pkg = functools.partialmethod(cmd2.Cmd.delimiter_complete,
    #                                             match_against=config.paths,
    #                                             delimiter='/')

    @with_argparser(bxt_move_args)
    def do_move_pkg(self, args):
        """
        Move one or more package(s) in bxt storage
        :param args: the package(s) to move from source to target
        """
        self.poutput("TODO: implement move")

    # complete_move_pkg = functools.partialmethod(cmd2.Cmd.delimiter_complete,
    #                                             match_against=config.paths,
    #                                             delimiter='/')

    @with_argparser(bxt_workspace_args)
    def do_workspace(self, args):
        """
        Get or set workspace
        :param args: optional path to new workspace
        """
        if not args.workspace:
            self.poutput(f"Current workspace is: {self.config.workspace}")
        else:
            ws_path = fix_path(args.workspace)
            ws = BxtWorkspace(ws_path, self.config.repos)
            if ws.init_repo_tree():
                self.poutput(f"Workspace {ws_path} created")
                self.config.workspace = ws_path
                self.config.save()
            else:
                self.perror(F"No permission on workspace: {ws_path}")

    @with_argparser(bxt_list_workspace_args)
    def do_list_workspace(self, args):
        """
        List content of current workspace
        """
        self.poutput("Current workspace is: " + self.config.workspace)
        cmd = ["ls"]
        if args.long:
            cmd.insert(len(cmd) + 1, "-l")
        cmd.insert(len(cmd) + 1, self.config.workspace)
        subprocess.run(cmd)

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

    # complete_list_repo = functools.partialmethod(cmd2.Cmd.delimiter_complete,
    #                                              match_against=config.paths,
    #                                              delimiter='/'
    #                                              )

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
            compare_us.append({"branch": branch, "repository": repository, "architecture": architecture})

        # send request
        compare_us = sorted(compare_us, key=lambda x: x["repository"])
        result = self.bxt_session.compare(
            url=f"{self.config.get_url()}/{self.config.endpoint["pkgCompare"]}",
            data=compare_us,
            token=self.config.get_access_token())
        print(result)
        compare_table = result.content()["compareTable"]
        pkgname_len = max(len(elm) for elm in compare_table) + 1

        pkg_list = []
        table_headers = []
        for target in compare_us:
            content = f"{target['branch']}/{target['repository']}/{target['architecture']}"
            table_headers.append(content)

        table_header_len = max(len(elm) for elm in table_headers) + 1
        compare_header = f"{"Packages":<{pkgname_len}}"
        for table_header in table_headers:
            compare_header += f"{table_header:>{table_header_len}}"

        for k, package in enumerate(compare_table.items()):
            pkg = {"name": package[0], "versions": []}
            pkg_versions = package[1]
            for key in pkg_versions.keys():
                if package[1][key] not in pkg["versions"]:
                    try:
                        pkg["versions"].append({"location": key, "version": package[1][key]["overlay"]})
                    except KeyError:
                        pkg["versions"].append({"location": key, "version": package[1][key]["automated"]})
            missing = [x for x in table_headers if x not in pkg_versions.keys()]
            for m in missing:
                pkg["versions"].append({"location": m, "version": "-"})
            # sort the version list for presentation
            pkg["versions"] = list(sorted(pkg["versions"], key=lambda x: x["location"]))
            pkg_list.append(pkg)

        pkg_list = sorted(pkg_list, key=lambda x: x["name"])
        # ------------ print result to screen -------------------------
        print(compare_header)
        print('-' * len(compare_header))

        for pkg in pkg_list:
            pkg_name = pkg["name"]
            pkg_versions = pkg["versions"]
            print(f"{pkg_name:<{pkgname_len}}", end="")
            for table_header in table_headers:
                version = next((v["version"] for v in pkg_versions if v["location"] == table_header), "-")
                print(f"{version:>{table_header_len}}", end="")
            print()

    # complate_compare_repo = functools.partialmethod(cmd2.Cmd.delimiter_complete,
    #                                                 match_against=config.paths,
    #                                                 delimiter='/'
    #                                                 )

    @with_argparser(bxt_upload_args)
    def do_upload(self, args):
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
        # packages = args.package
        self.quiet = False
        # self.pfeedback(f"TODO - commit package to repo - using {packages}")
        self.pfeedback(f"Reading files from workspace: {self.config.workspace}")
        self.pfeedback(f"Commit endpoint is: {self.config.endpoint['pkgCommit']}")
        self.pfeedback(f"Commit package(s) to: {branch}/{repo}/{arch}")
        # for pkg in packages:
        #     self.pfeedback(f"commit package: {pkg}")
        self.quiet = True

    # complete_upload = functools.partialmethod(cmd2.Cmd.delimiter_complete,
    #                                           match_against=config.paths,
    #                                           delimiter='/'
    #                                           )

    def do_login(self, args):
        """
        Retrieve JWT credentials for the configured bxt service
        """
        if not self.config.login():
            self.perror("Login failed!")
        # update prompt
        self.prompt = f"({self.config.get_name()}@{self.config.get_hostname()}) $ "

    def do_configure(self, args):
        """
        Configure endpoint and credentials
        """
        if not self.config.configure():
            self.perror("Configuration failed!")
        # update prompt
        self.prompt = f"({self.config.get_name()}@{self.config.get_hostname()}) $ "


def start_cmd2():
    """
    Poetry entry point
    :return:
    """
    if sys.platform.startswith("win"):
        print(f"unsupported operating system: {sys.platform}")
        exit(255)
    app = BxtCtl()
    sys.exit(app.cmdloop())


def main():
    """
    parse command line arguments and start application
    :return:
    """
    cfg = BxtConfig()
    # if config is uninitialized force setup config
    if cfg.get_url() == "" or cfg.get_name() == "":
        print("Enter initial configuration")
        if not cfg.configure():
            print("Initialization failed")
            exit(1)

    # if token is empty - login
    if cfg.get_access_token() == "":
        print("First time login")
        if not cfg.login():
            print("Login failed")
            exit(1)

    # initialize a session object
    bxt_session = BxtSession(BxtConfig.user_agent)
    sections = bxt_session.get_sections(
        f"{cfg.get_url()}/{BxtConfig.endpoint['pkgSection']}",
        cfg.get_access_token(),
    )
    acl = BxtAcl(sections)
    cfg.repos = path_completion(acl.get_branches, acl.get_repositories, acl.get_architectures)

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--set-ws", help="Set active workspace. The full path to the workspace")
    parser.add_argument("-g", "--get-ws", action="store_true", help="Get active workspace")
    parser.add_argument("-c", "--commit", type=str, nargs='?', default="*", const="*", help=f"Commit packages")
    parser.add_argument("--debug", action="store_true", help="Create logfile")
    parser.add_argument("-i", "--interactive", action="store_true", help="Load interactive shell")

    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        exit(1)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.get_ws:
        print(cfg.workspace)
        exit(0)

    if args.set_ws:
        cfg.workspace = fix_path(parser.parse_args().set_ws)
        ws = BxtWorkspace(cfg.workspace, cfg.repos)
        if not ws.init_repo_tree():
            logging.error(f"Failed to initialize workspace: {cfg.workspace}")
            exit(1)
        print(f"Workspace set to: {cfg.workspace}")
        cfg.save()
        exit(0)

    if args.commit:
        ws = BxtWorkspace(cfg.workspace, cfg.repos)
        if not ws.init_repo_tree():
            logging.error(f"Workspace has not been initialized: {cfg.workspace}")
            exit(1)
        if args.commit != "*":
            print(f"checking '{args.commit}'", end="\r")
            files = ws.get_packages(args.commit)
            if len(files) > 0:
                print(f"Uploading repo: '{args.commit}'")
                file_count = 0
                for file in files:
                    if file.sig is None:
                        print(f"'{file.pkg()}' has no signature... skipping", end="\n")
                        continue

                    print(f"Sending -> {file.pkg()}...", end="\n")
                    encoded = encode_package_data(file)
                    multipart_data = MultipartEncoder(fields=encoded)

                    logging.debug(multipart_data.content_type)
                    logging.debug(multipart_data.to_string())

                    result = bxt_session.commit(url=f"{cfg.get_url()}/{cfg.endpoint["pkgCommit"]}",
                                                data=multipart_data,
                                                token=cfg.get_access_token(),
                                                headers={"Content-Type": multipart_data.content_type}
                                                )
                    if result.status() != 200:
                        print(f"Failed to upload '{file.pkg()}' -> '{result.status()}'")
                        print(f"{result.content()}")
                        exit(1)
                    else:
                        file_count += 1

                print(f"Done! {file_count} packages uploaded to '{args.commit}'")

            else:
                print(f"Nothing to do in '{args.commit}'")

        else:
            print("checking all repos", end="\r")
            for repo in cfg.repos:
                files = ws.get_packages(repo)
                if len(files) > 0:
                    print(f"Uploading repo: '{repo}'")
                    file_count = 0
                    for file in files:
                        if file.sig is None:
                            print(f"'{file.pkg()}' has no signature... skipping", end="\n")
                            continue
                        print(f"Sending -> {file.pkg()}", end="\n")
                        file_count += 1
                    print(f"Done! {file_count} packages uploaded to '{args.commit}'")
                else:
                    print(f"Nothing to do in '{repo}'")
        exit(0)

    if args.interactive:
        start_cmd2()

if __name__ == "__main__":
    """
    Main entry point
    """
    main()
