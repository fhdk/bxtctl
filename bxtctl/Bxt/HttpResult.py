# -*- coding: utf-8 -*-
#
# bxtctl is a command line client designed to interact
# with bxt api which can be found at https://gitlab.com/anydistro/bxt
#
# BxtCtl is free software: you can redistribute it and/or modify
# it under the terms of the Affero GNU General Public License
# as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# BxtCtl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
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

from typing import Dict, Any, List


class HttpResult:
    """
    HTTP response class
    """

    def __init__(self, status: int, content: Dict[str, Any]):
        """
        Constructor
        :param content:
        :param status:
        """
        self._content = content
        self._status = status

    def content(self) -> Dict[str, Any]:
        """
        Response content
        :return:
        """
        return self._content

    def status(self) -> int:
        """
        Response status code
        :return:
        """
        return self._status

    def get(self):
        """
        Response as dict
        :return:
        """
        return {"json": self._content, "status": self._status}

    def __str__(self) -> str:
        """
        Response as string
        :return:
        """
        return f"Status: {self._status}, Content: '{self._content}'"
