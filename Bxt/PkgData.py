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
from .PkgFiles import PkgFiles
from .PkgInfo import PkgInfo


class Package:
    """
    Package commit object
    """

    def __init__(self, files: PkgFiles, info: PkgInfo):
        self._files = PkgFiles
        self._info = PkgInfo

    def set_file(self, files: PkgFiles):
        self._files = files

    def set_info(self, info: PkgInfo):
        self._info = info

    def get(self):
        return {"repo": self._files, "info": self._info}
