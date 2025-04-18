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
import unittest
from bxtctl.Bxt.BxtToken import BxtToken


class Test0001BxtToken(unittest.TestCase):
    def setUp(self):
        self.test_token = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXUyJ9.eyJleHAiOjE3MjU2MDA5MDAsImlhdCI6MTcyNTYwMDAwMCwiaXNzIjoiYnh0ZCIsImtpbmQiOiJhY2Nlc3NfdG9rZW4iLCJzdG9yYWdlIjoiYmVhcmVyIiwidXNlcm5hbWUiOiJieHR1c2VyIn0.wgar5KEEUR5j9ePPgCKaqHDwUedKtvKyZwGqUfwH3s4",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXUyJ9.eyJleHAiOjE3MjY2MDAwMDAsImlhdCI6MTcyNTYwMDAwMCwiaXNzIjoiYnh0ZCIsImtpbmQiOiJyZWZyZXNoX3Rva2VuIiwic3RvcmFnZSI6ImJlYXJlciIsInVzZXJuYW1lIjoiYnh0dXNlciJ9.ZjzWG91Qxk64KTqp_QnvkX0oAX88ql9QvyFHFm-uSgQ",
            "token_type": "bearer",
        }

        self.test_token_payload = {
            "exp": 1725600900,
            "iat": 1725600000,
            "iss": "bxtd",
            "kind": "access_token",
            "storage": "bearer",
            "username": "bxtuser",
        }
        self.test_refresh_payload = {
            "exp": 1726600000,
            "iat": 1725600000,
            "iss": "bxtd",
            "kind": "refresh_token",
            "storage": "bearer",
            "username": "bxtuser",
        }

        self.token = BxtToken(self.test_token)

    def test_get_access_token(self):
        """
        Test get access token
        :return:
        """
        token = self.token.get_access_token()
        assert token == self.test_token["access_token"]

    def test_get_refresh_token(self):
        """
        Test get refresh token
        :return:
        """
        token = self.token.get_refresh_token()
        assert token == self.test_token["refresh_token"]

    def test_token_owner(self):
        """
        Test if the token belong is the expected owner
        :return:
        """
        assert self.token.validate_owner("bxtuser") == True

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
