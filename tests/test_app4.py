import unittest
import requests
from bs4 import BeautifulSoup

server_address = "http://127.0.0.1:5000"
server_login = server_address + "/login"
server_register = server_address + "/register"

def getElementById(text, eid):
    soup = BeautifulSoup(text, "html.parser")
    result = soup.find(id=eid)
    return result


def register(uname, pword, mfa, login="Register Now", session=None, ctoken=None):
    if session is None:
        session = requests.Session()

    r = session.post(server_register)

    if ctoken is None:
        ctoken = getElementById(r.text, "csrf_token")
        ctoken = ctoken['value']

    test_creds = {"csrf_token": ctoken, "username": uname, "password": pword, "2fa": mfa, "submit": login}
    print(test_creds)
    r = session.post(server_register, data=test_creds)


    success = getElementById(r.text, "success")
    print (success)
    print("*********")
    print(r.text)
    assert success is not None, "Missing id='sucess' in your login response"
    return "wrong" in str(success).split(" ")


class FeatureTest(unittest.TestCase):
    def test_register(self):
        resp = register( "meir", "12345", "123", "Register Now")
        print("k1")
        print(resp)
        self.assertFalse(resp, "A unique username is needed! - Success")

