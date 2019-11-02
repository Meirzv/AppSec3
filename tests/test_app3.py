import unittest
import requests
from bs4 import BeautifulSoup

server_address = "http://127.0.0.1:5000"
server_login = server_address + "/login"
server_spellcheck = server_address + "/spell_check"


def getElementById(text, eid):
    soup = BeautifulSoup(text, "html.parser")
    result = soup.find(id=eid)
    return result


def login(uname, pword, mfa, login="Login", session=None):
    if session is None:
        session = requests.Session()

    r = session.post(server_login)

    ctoken = getElementById(r.text, "csrf_token")
    ctoken = ctoken['value']

    test_creds = {"csrf_token": ctoken, "username": uname, "password": pword, "2fa": mfa, "submit": login}
    r = session.post(server_login, data=test_creds)

    success = getElementById(r.text, "result")

 #   print(r.text)

    assert success is not None, "Missing id='result' in your login response"
    return session


def spell_check(session, ctoken = None, command= None):

    r = session.post(server_spellcheck)

    if ctoken is None:
        ctoken = getElementById(r.text, "csrf_token")
        ctoken = ctoken['value']

    if command is None:
        command = "No"
    else:
        command = "meirzeevi"


    print(r.text)
    spell_check_data = {"csrf_token": ctoken, "command": command, "submit": "Go!"}

    r = session.post(server_spellcheck, data=spell_check_data)

    misspelled_note = getElementById(r.text, "misspelled")
    print("hi")
    print(r.text)
    print("********************")
    print(misspelled_note)
    return command in str(misspelled_note).split(" ")

class FeatureTest(unittest.TestCase):
    def test_spell_check_with_wrong_csrftoken_after_login(self):
        session = login( "meir", "12345", "123", "Login")
        resp = spell_check(session, "faketoken")
        print("k1")
        print(resp)
        self.assertFalse(resp, "Success! CSRF attack was prevented!")

    def test_spell_check_with_correct_csrftoken_after_login_misspelled_output(self):
        session = login( "meir", "12345", "123", "Login")
        resp = spell_check(session, None, "few word meirzeevi")
        print("k1")
        print(resp)
        self.assertTrue(resp, "Success! The correct misspelled words is presented")

    def test_spell_check_with_correct_csrftoken_after_login_no_misspelled_output(self):
        session = login( "meir", "12345", "123", "Login")
        resp = spell_check(session, None)
        print("k1")
        print(resp)
        self.assertTrue(resp, "Success! The correct misspelled words is presented")