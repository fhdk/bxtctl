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

from typing import List
from pathlib import Path
import glob
import os
import logging

# app supplied sources
from .BxtFile import BxtFile


class BxtWorkspace:

    def __init__(self, path: str, repos: List[str]):
        """
        BxtWorkspace
        """
        self._path = path
        self._repos = repos

    def valid_workspace(self) -> bool:
        """
        Check workspace structure
        :return:
        """
        for repo in self._repos:
            if not os.path.exists(f"{self._path}/{repo}"):
                logging.error(f"Repo {repo} has not been fully initialized!")
                return False
        return True

    def get_packages(self, repo: str) -> List[BxtFile]:
        """
        Get the files from the given repository
        :param repo:
        :return:
        """
        result = []
        if not repo in self._repos:
            logging.error(f"The '{repo}' was not found in repos {self._repos}")
            return result
        section = self.get_section_from_repo(repo)
        repo_dir = f"{self._path}/{repo}"
        # glob for getting only package files from repo_dir
        package_glob = f"{repo_dir}/*.pkg.tar.zst"
        # generate a list of files
        package_list = filter(lambda x: os.path.isfile, glob.glob(package_glob))
        # sort files by size - largest files first
        files = sorted(package_list, key=lambda x: os.stat(os.path.join(repo_dir, x)).st_size, reverse=True)
        # loop the files and build a list of BxtFile objects
        for file in files:
            bxt_file = BxtFile(
                section,
                f"{file}",
                f"{file}.sig",
            )
            # verify if signature is present
            if not os.path.exists(bxt_file.signature):
                # clear signature - filename is not valid
                bxt_file.signature = None
            result.append(bxt_file)
        return result

    @staticmethod
    def get_section_from_repo(repo: str) -> dict:
        """
        Get the section from the given repository
        :param repo:
        :return:
        """
        data = repo.split("/")
        return {
            "branch": data[0],
            "repository": data[1],
            "architecture": data[2],
        }

    def init_workspace(self) -> bool:
        """
        Initialize workspace structure
        :return:
        """
        try:
            for repo in self._repos:
                logging.debug("Path: " + repo)
                Path(f"{self._path}/{repo}").mkdir(parents=True, exist_ok=True)
            return True
        except PermissionError:
            logging.error(f"You do not have write permissions: {self._path}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return False

    @staticmethod
    def pkg_remove(file: BxtFile):
        """
        Remove package files after successful upload
        :param file:
        :return:
        """
        try:
            os.remove(file.package)
            os.remove(file.signature)
        except FileNotFoundError:
            pass
