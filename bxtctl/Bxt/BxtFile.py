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

from typing import Dict


class BxtFile:
    """
    BxtFile object
    """

    def __init__(
        self, section: Dict[str, str], package: str, signature: str, size: int
    ):
        self._section = section
        self._package = package
        self._signature = signature
        self._size = size

    @property
    def section(self):
        """
        Get Section
        :return:
        """
        return self._section

    @property
    def package(self):
        """
        Get Package File Name and Path
        :return: 
        """ ""
        return self._package

    @property
    def signature(self):
        """
        Get Signature File Name
        :return:
        """
        return self._signature

    @signature.setter
    def signature(self, signature: str):
        """
        Set Signature File Name
        :param signature:
        :return:
        """
        self._signature = signature

    @property
    def size(self):
        """
        Get ghe package size
        """
        return self._size

    def __str__(self):
        return f"Package: '{self._package}', Signature: '{self._signature}', Section: '{self._section}', Size: '{self._size}'"
