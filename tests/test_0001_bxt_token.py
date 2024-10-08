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
        Test if token is the expected owner
        :return:
        """
        assert self.token.validate_owner("bxtuser") == True


    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
