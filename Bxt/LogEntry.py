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
from .Package import Package


class LogEntry:
    def __init__(self, logid: str, time: int, package: Package, entrytype: str):
        self._id = logid
        self._time = time
        self._package = package
        self._entrytype = entrytype

    def get(self):
        return {
            "id": self._id,
            "time": self._time,
            "package": self._package,
            "type": self._entrytype,
        }

    # [
    #   {
    #     "id": "string",
    #     "time": 0,
    #     "type": "Add",
    #     "package": {
    #       "name": "string",
    #       "section": "string",
    #       "poolEntries": {
    #         "additionalProp1": {
    #           "version": "string",
    #           "signaturePath": true
    #         },
    #         "additionalProp2": {
    #           "version": "string",
    #           "signaturePath": true
    #         },
    #         "additionalProp3": {
    #           "version": "string",
    #           "signaturePath": true
    #         }
    #       },
    #       "preferredLocation": "string"
    #     }
    #   }
    # ]
