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

from .Section import Section
from .PoolEntry import PoolEntry


class Package:
    """
    A package list entry
    """

    def __init__(
        self,
        name: str,
        section: Section,
        poolentries: [PoolEntry],
        preferred_location: str,
    ):
        self._name = name
        self._section = section
        self._pool_entries = poolentries
        self._preferred_location = preferred_location

    def get(self):
        return {
            "name": self._name,
            "section": self._section,
            "poolEntries": self._pool_entries,
            "preferredLocation": self._preferred_location,
        }


# {
# "name": "string",
# "section": "string",
# "poolEntries": {
#   "additionalProp1": {
#     "version": "string",
#     "signaturePath": true
#   },
#   "additionalProp2": {
#     "version": "string",
#     "signaturePath": true
#   },
#   "additionalProp3": {
#     "version": "string",
#     "signaturePath": true
#   }
# },
# "preferredLocation": "string"
# }