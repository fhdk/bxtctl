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

from typing import Dict

class BxtFile:
    """
    BxtFile object
    """
    def __init__(self, section: Dict[str,str], pkg: str, sig: str):
        self._section = section
        self._pkg = pkg
        self._sig = sig

    def section(self):
        """
        Get Section
        :return:
        """
        return self._section

    def pkg(self):
        """
        Get Package File Name and Path
        :return: 
        """""
        return self._pkg

    @property
    def sig(self):
        """
        Get Signature File Name
        :return:
        """
        return self._sig

    @sig.setter
    def sig(self, sig: str):
        """
        Set Signature File Name
        :param sig:
        :return:
        """
        self._sig = sig

