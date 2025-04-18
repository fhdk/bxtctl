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
import argparse
import sys
import logging

# app supplied sources
from bxtctl.Bxt.BxtAcl import BxtAcl
from bxtctl.Bxt.BxtConfig import BxtConfig
from bxtctl.Bxt.BxtSession import BxtSession
from bxtctl.Bxt.Utils import path_completion, fix_path, encode_package_data
from bxtctl.Bxt.BxtWorkspace import BxtWorkspace


# cfg = BxtConfig()
# if not cfg.valid_config():
#     cfg.configure()
#
# if not cfg.get_access_token():
#     z = cfg.login()
#
# if cfg.valid_token():
#     if not cfg.renew_access_token():
#         z = cfg.login()
#
# # setup basic logging
# logging.basicConfig(level=logging.INFO, filename=f"{fix_path(cfg.config_dir)}/bxtcmd.log", encoding="utf-8")
#
# # initialize a session object
# bxt_session = BxtSession(cfg.user_agent)
#
# # read sections for the current user from the bxt service endpoint
# sections = bxt_session.get_sections(f"{cfg.get_url()}/{cfg.endpoint['pkgSection']}", cfg.get_access_token())
#
# # set up the access control
# acl = BxtAcl(sections)
#
# # create a path completion object and store in configuration
# cfg.repos = path_completion(acl.get_branches, acl.get_repositories, acl.get_architectures)
#
# # ensure workspace has been initialized
# ws = BxtWorkspace(cfg.get_workspace(), cfg.repos)
# if not ws.init_workspace():
#     ws.init_workspace()

bxt_cmds = argparse.ArgumentParser()
cmds_exclusive = bxt_cmds.add_mutually_exclusive_group()
cmds_exclusive.add_argument("rm", type=str, nargs="*", help="remove packages")
cmds_exclusive.add_argument("ls", type=str, nargs="*", help="list packages")
cmds_exclusive.add_argument("commit", type=str, nargs="*", help="add packages")

args = bxt_cmds.parse_args()

print(args)
