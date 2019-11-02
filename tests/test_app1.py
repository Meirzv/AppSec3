import unittest
import requests
from bs4 import BeautifulSoup

server_address = "http://127.0.0.1:5000"
server_login = server_address + "/login"


def getElementById(text, eid):
    soup = BeautifulSoup(text, "html.parser")
    result = soup.find(id=eid)
    return result


def login(uname, pword, mfa, login="Login", session=None, ctoken=None):
    if session is None:
        session = requests.Session()

    r = session.post(server_login)

    if ctoken is None:
        ctoken = getElementById(r.text, "csrf_token")
        ctoken = ctoken['value']

    test_creds = {"csrf_token": ctoken, "username": uname, "password": pword, "2fa": mfa, "submit": login}
    print(test_creds)
    r = session.post(server_login, data=test_creds)

    if ctoken != "faketoken":
        success = getElementById(r.text, "result")
    else:
        success = "something" #should not have any value if csrf token is not correct
    print(r.text)

    assert success is not None, "Missing id='result' in your login response"
    return "success" in str(success).split(" ")


class FeatureTest(unittest.TestCase):
    def test_valid_login(self):
        resp = login( "meir", "12345", "123", "Login")
        print("k1")
        print(resp)
        self.assertTrue(resp, "Success! User is logged in")

    def test_invalid_login(self):
        resp = login("test", "notpassword", "None","Login")
        self.assertFalse(resp, "Invalid username or password - Success!")

    def test_valid_login_invalid_csrf_token(self):
        resp = login( "meir", "12345", "123", "Login", None , "faketoken")
        print("k2")
        print(resp)
        self.assertFalse(resp, "Cannot login because an invalid csrf_token - Success!")