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
class PkgInfo:
    """
    The info part of a package commit
    """

    def __init__(self, name: str, branch: str, repository: str, architecture: str):
        self._name = name
        self._branch = branch
        self._repository = repository
        self._architecture = architecture

    def get(self):
        return {
            "name": self._name,
            "branch": self._branch,
            "repository": self._repository,
            "architecture": self._architecture,
        }


# [
#     {
#         "name": "string",
#         "section": "string",
#         "poolEntries": {
#             "additionalProp1": {
#                 "version": "string",
#                 "signaturePath": true
#             },
#             "additionalProp2": {
#                 "version": "string",
#                 "signaturePath": true
#             },
#             "additionalProp3": {
#                 "version": "string",
#                 "signaturePath": true
#             }
#         },
#         "preferredLocation": "string"
#     }
# ]
