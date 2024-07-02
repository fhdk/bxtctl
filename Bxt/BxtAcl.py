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
from .Section import Section


class BxtAcl:
    """
    Bxt Access Control List
    """

    def __init__(self, sections: [Section]):
        """
        Initialize ACL using a sections object
        :param sections:
        """
        self._sections = sections

    def get(self):
        return self._sections

    def get_architectures(self) -> set:
        """
        Return architectures available in the ACL
        :return:
        """
        architectures = []
        for section in self._sections:
            architectures.append(section["architecture"])
        return set(architectures)

    def get_branches(self):
        """
        Return branches available in the ACL
        :return:
        """
        branches = []
        for section in self._sections:
            branches.append(section["branch"])
        return set(branches)

    def get_repositories(self):
        """
        Return repositories available in the ACL
        :return:
        """
        repositories = []
        for section in self._sections:
            repositories.append(section["repository"])
        return set(repositories)
