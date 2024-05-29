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

class User:
    """
    User ACL object
    """
    def __init__(self, name: str, permissions: [str]):
        self._name = name
        self._permissions = permissions
        self._password = None

    def update(self, new_pass: str, new_permissions: [str]):
        self._permissions = new_permissions
        self._password = new_pass

    def get(self):
        return {
            "name": self._name,
            "password": self._password,
            "permissions": self._permissions
        }

# {
#   "name": "string",
#   "password": "string",
#   "permissions": [
#     "string"
#   ]
# }
