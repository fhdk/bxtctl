#!/usr/bin/env python3
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

import time
from Bxt.BxtConfig import BxtConfig
from Bxt import BxtSession

"""
Get a list of packages from 
from: stable -> extra -> x86_64 repo
"""

config = BxtConfig()

if not config.valid_config():
    y = config.configure()

if not config.get_access_token():
    config.login()

if config.valid_token():
    if not config.renew_access_token():
        z = config.login()

token = config.get_access_token()
endpoint = f"{config.get_url()}/{config.endpoint["pkgCompare"]}"
http = BxtSession(config.user_agent)

print("bxt_compare : ")
print("compare request begin    --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
compare_repo = [
    {"branch": "unstable", "repository": "core", "architecture": "x86_64"},
    {"branch": "unstable", "repository": "extra", "architecture": "x86_64"},
    {"branch": "unstable", "repository": "multilib", "architecture": "x86_64"},
]

compare_repo = sorted(compare_repo, key=lambda x: x["repository"])

result = http.compare(url=endpoint, data=compare_repo, token=config.get_access_token())
print("compare request response --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
print("result : {}".format(result))
print("------------")
print("compare request parsing  --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
compare_table = result.content()["compareTable"]
pkgname_len = max(len(elm) for elm in compare_table) + 1

pkg_list = []
table_headers = []
for target in compare_repo:
    content = f"{target['branch']}/{target['repository']}/{target['architecture']}"
    table_headers.append(content)
table_header_len = max(len(elm) for elm in table_headers) + 1
compare_header = f"{"Packages":<{pkgname_len}}"
for table_header in table_headers:
    compare_header += f"{table_header:>{table_header_len}}"

for k, package in enumerate(compare_table.items()):
    pkg = {"name": package[0], "versions": []}
    pkg_versions = package[1]
    for key in pkg_versions.keys():
        if package[1][key] not in pkg["versions"]:
            try:
                pkg["versions"].append(
                    {"location": key, "version": package[1][key]["overlay"]}
                )
            except KeyError:
                pkg["versions"].append(
                    {"location": key, "version": package[1][key]["automated"]}
                )
    missing = [x for x in table_headers if x not in pkg_versions.keys()]
    for m in missing:
        pkg["versions"].append({"location": m, "version": "-"})
    # sort the version list for presentation
    pkg["versions"] = list(sorted(pkg["versions"], key=lambda x: x["location"]))
    pkg_list.append(pkg)

pkg_list = sorted(pkg_list, key=lambda x: x["name"])
# ------------ test print result to screen -------------------------
print(compare_header)
print("-" * len(compare_header))

for pkg in pkg_list:
    pkg_name = pkg["name"]
    pkg_versions = pkg["versions"]
    print(f"{pkg_name:<{pkgname_len}}", end="")
    for table_header in table_headers:
        version = next(
            (v["version"] for v in pkg_versions if v["location"] == table_header), "-"
        )
        print(f"{version:>{table_header_len}}", end="")
    print()
