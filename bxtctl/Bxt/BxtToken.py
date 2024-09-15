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

import jwt
import time

from .BxtException import BxtException

OPTIONS = {"verify_signature": False}
ALGORITHMS = ["HS256"]

# TODO catch JWT parsing errors
# TODO raise an BxtExeption instance on JWT parsing errors


class BxtToken:
    access_token: str = ""
    refresh_token: str = ""
    token_type: str = ""

    def __init__(self, token: dict = None):
        if token:
            try:
                self.access_token = token["access_token"]
                self.refresh_token = token["refresh_token"]
                self.token_type = token["token_type"]
            except KeyError:
                raise BxtException(
                    msg="Invalid token format",
                    errors="One or more elements could not be parsed from the token",
                )

    def __str__(self):
        return f"BxtToken (Access Token: '{self.access_token}', Refresh Token: '{self.refresh_token}', Token Type: '{self.token_type}')"

    def get(self):
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
        }

    def get_access_expiration(self) -> int:
        """
        return time to access token expiration
        :return:
        """
        decoded = jwt.decode(self.access_token, algorithms=ALGORITHMS, options=OPTIONS)
        expiration_time = decoded.get("exp")
        current_time = int(time.time())
        return expiration_time - current_time

    def get_access_expired(self) -> bool:
        """
        check if access token has expired
        :return:
        """
        decoded = jwt.decode(self.access_token, algorithms=ALGORITHMS, options=OPTIONS)
        expiration_time = decoded.get("exp")
        current_time = int(time.time())
        return expiration_time < current_time

    def get_access_token(self) -> str:
        """
        get access token
        :return:
        """
        return self.access_token

    def get_refresh_expiration(self) -> int:
        """
        return time to refresh token expiriration
        :return:
        """
        decoded = jwt.decode(self.access_token, algorithms=ALGORITHMS, options=OPTIONS)
        expiration_time = decoded.get("exp")
        current_time = int(time.time())
        return current_time - expiration_time

    def get_refresh_expired(self) -> bool:
        """
        check if refresh token has expired
        :return:
        """
        decoded = jwt.decode(self.refresh_token, algorithms=ALGORITHMS, options=OPTIONS)
        expiration_time = decoded.get("exp")
        current_time = int(time.time())
        return expiration_time < current_time

    def get_refresh_token(self) -> str:
        """
        get refresh token
        :return:
        """
        return self.refresh_token

    def get_token_type(self) -> str:
        """
        get token type
        :return:
        """
        return self.token_type

    def validate_owner(self, bxt_owner: str) -> bool:
        """
        get the token owner
        :return:
        """
        decoded = jwt.decode(self.refresh_token, algorithms=ALGORITHMS, options=OPTIONS)
        return decoded["username"] == bxt_owner
