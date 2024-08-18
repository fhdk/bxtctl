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
from logging import fatal
from typing import List, Dict
from pathlib import Path
import os
import logging

class BxtWorkspace:
    def __init__(self, path: str, repos: List[str]):
        """
        BxtWorkspace
        """
        self._path = path
        self._repos = repos

    def check_workspace(self) -> bool:
        """
        Check workspace structure
        :return:
        """
        for repo in self._repos:
            if not os.path.exists(f"{self._path}/{repo}"):
                logging.error(f"Repo {repo} has not been fully initialized!")
                return False
        return True

    def get_files(self, path: str = None) -> list:
        """
        Get the files from the given path
        :return:
        """
        result = []
        if not path in self._repos:
            logging.error(f"Path {path} not in repos {self._repos}")
            return result

        if path is not None:
            for file in os.listdir(path):
                if file.endswith(".pkg.tar.zst"):
                    result.append({
                        "pkg": f"{self._path}/{path}/{file}",
                        "sig": f"{self._path}/{path}/{file}.sig"}
                    )
            return result

        for repo in self._repos:
            for file in os.listdir(f"{self._path}/{repo}"):
                if file.endswith(".pkg.tar.zst"):
                    result.append({
                        "pkg": f"{self._path}/{repo}/{file}",
                        "sig": f"{self._path}/{repo}/{file}.sig"}
                    )

        return result

    def init_workspace_tree(self) -> bool:
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
