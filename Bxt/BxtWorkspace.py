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
    def __init__(self, path: str, permissions: List[str]):
        """
        BxtWorkspace
        """
        self._path = path
        self._permissions = permissions

    def init_workspace_structure(self) -> bool:
        """
        Initialize workspace structure
        :return:
        """
        try:
            for perm in self._permissions:
                logging.debug("Path: " + perm)
                Path(f"{self._path}/{perm}").mkdir(parents=True, exist_ok=True)
            return True
        except PermissionError:
            logging.error(f"You do not have write permissions: {self._path}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return False

    def get_files(self) -> list:
        """
        Get the files from the given path
        :return:
        """
        result = []
        for perm in self._permissions:
            for file in os.listdir(f"{self._path}/{perm}"):
                if file.endswith(".pkg.tar.zst"):
                    result.append({
                        "pkg": f"{self._path}/{perm}/{file}",
                        "sig": f"{self._path}/{perm}/{file}.sig"}
                    )
        return result

    # def check_workspace(ws_path: str, permissions: List[str]) -> bool:
    #     """
    #     Check workspace match permisions.
    #     :param ws_path:
    #     :param permissions:
    #     :return:
    #     """
    #     for perm in permissions:
    #         try:
    #             if not os.path.exists(os.path.join(ws_path, perm)):
    #                 os.makedirs(os.path.join(ws_path, perm))
    #             return True
    #         except FileExistsError as err:
    #             logging.debug(err)
    #         except FileNotFoundError as err:
    #             logging.debug(err)
    #         except NotADirectoryError as err:
    #             logging.debug(err)
    #
    #     return False