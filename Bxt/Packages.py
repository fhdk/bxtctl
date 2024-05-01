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


class Packages:
    """
    A set of packages from a given branch, repo and architecture
    """
    def __init__(self, packages: [Package]):
        self._packages = packages

    def get(self) -> [Package]:
        """
        Get Packages
        :return:[{
                    "name": "string",
                    "section": {
                        "branch": "string",
                        "repository": "string",
                        "architecture": "string"
                     },
                     "pool_entries": [
                     {
                        "version": "string",
                        "hasSignature": true
                        }
                    ]
                }]
        """
        return self._packages

    def get_package(self, name: str) -> Package:
        """
        Get package from list
        :param name:
        :return:
        """
        pkgs = [x for x in self._packages if x["name"] == name]
        for pkg in pkgs:
            return pkg
