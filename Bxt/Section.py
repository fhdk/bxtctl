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
class Section:
    """
    Package Section info
    """

    def __init__(self, branch: str, repository: str, architecture: str):
        self._branch = branch
        self._repository = repository
        self._architecture = architecture

    def get(self):
        return {
            "branch": self._branch,
            "repository": self._repository,
            "architecture": self._architecture,
        }


# [
#   {
#     "branch": "string",
#     "repository": "string",
#     "architecture": "string"
#   }
# ]
