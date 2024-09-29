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
import os
import json
import requests
# app supplied sources
from .BxtFile import BxtFile


def check_connection(url: str) -> bool:
    """
    Check connection to host
    :param url:
    :return:
    """
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        return True
    return False


def encode_package_data(file: BxtFile, idx: int = 1):
    """
    Create dictionary to be consumed as multipart/form-data
    :param file:
    :param idx:
    :return:
    """
    pkgfile = file.package.split("/")[-1]
    sigfile = file.signature.split("/")[-1]
    return {
        (
            f"package{idx}",
            (pkgfile, open(file.package, "rb"), "application/octet-stream"),
        ),
        (
            f"package{idx}.signature",
            (sigfile, open(file.signature, "rb"), "application/octet-stream"),
        ),
        (f"package{idx}.section", (None, json.dumps(file.section), "text/plain")),
    }


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


def path_completion(branches, repositories, architectures) -> List[str]:
    """
    generate a list of path completions for bxt repo
    :param branches:
    :param repositories:
    :param architectures:
    :return:
    """
    result = []
    branches = list(branches())
    repositories = list(repositories())
    architectures = list(architectures())
    for branch in branches:
        for repo in repositories:
            for arch in architectures:
                result.append(f"{branch}/{repo}/{arch}")
    return result
