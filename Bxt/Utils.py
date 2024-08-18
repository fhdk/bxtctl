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
from typing import List
import os


def path_completion(branches, repos, archs) -> List[str]:
    """
    generate a list of path completions for bxt repo
    :param branches:
    :param repos:
    :param archs:
    :return:
    """
    result = []
    branches = list(branches())
    repos = list(repos())
    archs = list(archs())
    for branch in branches:
        for repo in repos:
            for arch in archs:
                result.append(f"{branch}/{repo}/{arch}")
    return result

def fix_path(path: str) -> str:
    """
    Expand home path
    :param path:
    :rtype: str
    :return: fixed path
    """
    if "~" in path:
        path = path.replace("~", os.path.expanduser("~"))
    return path

