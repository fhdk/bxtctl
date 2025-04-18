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

from bxtctl.Bxt.BxtSession import BxtSession
from bxtctl.Bxt.BxtAcl import BxtAcl
from bxtctl.Bxt.BxtConfig import BxtConfig
from bxtctl.Bxt.BxtWorkspace import BxtWorkspace
from bxtctl.Bxt.Utils import path_completion


"""
This file is to test the correct creating of a workspace
The workspace must populated with a folder tree matching the permissions
"""
config = BxtConfig()

if not config.valid_config():
    y = config.configure()

if not config.get_access_token():
    z = config.login()

# initialize a session object
bxt_session = BxtSession(BxtConfig.user_agent)
sections = bxt_session.get_sections(
    f"{config.get_url()}/{BxtConfig.endpoint['pkgSection']}",
    config.get_access_token(),
)

acl = BxtAcl(sections)

config.repos = path_completion(
    acl.get_branches, acl.get_repositories, acl.get_architectures
)

print(config.get_workspace())
print(config.repos)

ws = BxtWorkspace(config.get_workspace(), config.repos)

print("init_repos: ", ws.init_workspace())
