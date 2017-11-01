from Tests.test_setup import BaseTestClass
from app.models import User

import json

class UserRegisterTest(BaseTestClass):
    "Test Class for user registration"

    def test_user_registration(self):
        " Test that the user has been registered with valid information "
        initial = User.query.count()
        data = json.dumps({"username": "bob",
                           "password": "bobpass",
                           "email": "bob@example.com"})

        response = self.app.post("/api/v1/auth/register",
                                 data= data,
                                 content_type=self.mime_type)
        response_data = json.loads(response.data)

        final_data = User.query.count()
        self.assertEqual(response.status_code,201)
        self.assertEqual(final_data -initial,1)
        self.assertEqual(response_data["message"],("You have been successfully added as bob"))

    def test_register_existing_username(self):
        "Test that the users are unique"

        data = json.dumps({"username":"bob", "password":"bobpass", "email":"bob@example.com"})
        data_name = json.dumps({"username": "Bob", "password": "bobpass",
                                "email": "bob@example.com"})
        response = self.app.post("/api/v1/auth/register", data=data,
                                 content_type=self.mime_type)
        response_cap = self.app.post("/api/v1/auth/register", data=data_name,
                                     content_type=self.mime_type)

        resp_data = json.loads(response.data)
        respcap_data = json.loads(response_cap.data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_cap.status_code, 403)
        self.assertEqual(User.query.count(), 2)
        self.assertEqual(resp_data["message"], "username already taken")
        self.assertEqual(respcap_data["message"], "username already taken")

    def test_missing_details_for_register(self):
        """Test that the validation of an already existing user works"""
        data_nouser = json.dumps({"password": "bobpass",
                                  "email": "bob@example.com"})
        data_nopass = json.dumps({"username": "bob",
                                  "email": "bob@example.com"})
        data_noemail = json.dumps({"username": "bob",
                                   "password": "bobpass"})
        response_nouser = self.app.post("/api/v1/auth/register",
                                        data=data_nouser,
                                        content_type=self.mime_type)
        response_nopass = self.app.post("/api/v1/auth/register",
                                        data=data_nopass,
                                        content_type=self.mime_type)
        response_noemail = self.app.post("/api/v1/auth/register",
                                         data=data_noemail,
                                         content_type=self.mime_type)
        resp_nouser = json.loads(response_nouser.data)
        resp_nopass = json.loads(response_nopass.data)
        resp_noemail = json.loads(response_noemail.data)
        self.assertListEqual([400, 400, 400], [response_nouser.status_code,
                                               response_nopass.status_code,
                                               response_noemail.status_code])
        self.assertEqual(resp_nouser["message"]["username"],
                         "Enter a user name")
        self.assertEqual(resp_nopass["message"]["password"],
                         "Enter a password")
        self.assertEqual(resp_noemail["message"]["email"],
                         "Enter an email")

    def test_bad_details_for_registration(self):
        """test that username can't contain special characters"""
        data = json.dumps({"username": "#@!^", "password": "foobar",
                           "email": "foobar"})
        data_blank = json.dumps({"username": "sam", "password": " ",
                                 "email": "sam@example.com"})
        response = self.app.post("/api/v1/auth/register", data=data,
                                 content_type=self.mime_type)
        response_data_blank = self.app.post("/api/v1/auth/register",
                                            data=data_blank,
                                            content_type=self.mime_type)
        resp_data = json.loads(response.data)
        respblank_data = json.loads(response_data_blank.data)
        self.assertListEqual([400, 400], [response.status_code,
                                          response_data_blank.status_code])
        self.assertIn("only numbers, letters, '-','-','.' allowedin username entry", resp_data["message"])
        self.assertIn("password must be 6 characters", respblank_data["message"])
        self.assertEqual(User.query.count(), 2)

    def test_blank_arguments_not_allowed(self):
        """test that registration doesn't accept invalid arguments """
        blnk_nme = json.dumps({"username": "", "password": "foobar",
                               "email": "foobar@gmail.com"})
        blnk_pass = json.dumps({"username": "fooname", "password": "",
                                "email": "foobar@gmail.com"})
        blnk_mail = json.dumps({"username": "fooname", "password": "foobar",
                                "email": ""})

        resp_nme = self.app.post("/api/v1/auth/register", data=blnk_nme,
                                 content_type=self.mime_type)
        resp_pass = self.app.post("/api/v1/auth/register", data=blnk_pass,
                                  content_type=self.mime_type)
        resp_mail = self.app.post("/api/v1/auth/register", data=blnk_mail,
                                  content_type=self.mime_type)

        data_nme = json.loads(resp_nme.data)
        data_pass = json.loads(resp_pass.data)
        data_mail = json.loads(resp_mail.data)

        self.assertListEqual([400, 400, 400], [resp_nme.status_code,
                                               resp_pass.status_code,
                                               resp_mail.status_code])
        self.assertIn("allowedin username", data_nme["message"])
        self.assertIn("password must be", data_pass["message"])
        self.assertIn("Enter a valid email", data_mail["message"])
        self.assertEqual(User.query.count(), 2)

    def test_email_field_basic_validation(self):
        """test that the @ symbol must be present as a test of the email
        validation"""
        data = json.dumps({"username": "bob", "password": "bobpass",
                           "email": "bobexample.com"})
        response = self.app.post("/api/v1/auth/register", data=data,
                                 content_type=self.mime_type)
        resp_data = json.loads(response.data)
        self.assertEqual(400, response.status_code)
        self.assertEqual("Enter a valid email", resp_data["message"])

    def test_password_salts_are_random(self):
        """ test that hashing algorithm doesn't store equal passwords with an
        equal hash """
        user_one = User.query.filter_by(id=1).first()
        user_two = User.query.filter_by(id=2).first()
        self.assertTrue(user_one.password_hformat != user_two.password_hformat)

    def test_user_password_cant_be_read(self):
        """test that password attribute can't be directly accessed, is read
        only"""
        user_one = User.query.filter_by(id=1).first()
        with self.assertRaises(AttributeError):
            user_one.password

class UserLoginTest(BaseTestClass):
    """the tests for user login"""
    def test_successful_login(self):
        """test that user can login with valid details and gets token"""
        data = json.dumps({"username": "bob", "password": "bobpass"})
        response = self.app.post("api/v1/auth/login", data=data,
                                 content_type=self.mime_type)
        resp_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(resp_data["token"]) > 20)
    def test_unregistered_user_cant_get_token(self):
        """
        test that unregistered users can't obtain a token check credentials
        as well"""
        data = json.dumps({"username": "foobar", "password": "foobar"})
        response = self.app.post("api/v1/auth/login", data=data,
                                 content_type=self.mime_type)
        resp_data = json.loads(response.data)
        data_wrongpass = json.dumps({"username": "bob", "password": "bob"})
        response_wrongpass = self.app.post("api/v1/auth/login",
                                           data=data_wrongpass,
                                           content_type=self.mime_type)
        response_wrongpass_data = json.loads(response_wrongpass.data)
        self.assertListEqual([response.status_code,
                              response_wrongpass.status_code],
                             [401, 401])
        self.assertEqual(resp_data["message"], "wrong login details")
        self.assertEqual(response_wrongpass_data["message"],
                         "wrong login details")

    def test_missing_details_login(self):
        """ test that API catches missing keys errors """
        data_noname = json.dumps({"password": "bobpass"})
        data_nopass = json.dumps({"username": "bob"})
        resp_noname = self.app.post("api/v1/auth/login", data=data_noname,
                                    content_type=self.mime_type)
        resp_nopass = self.app.post("api/v1/auth/login", data=data_nopass,
                                    content_type=self.mime_type)
        resp_nonamedata = json.loads(resp_noname.data)
        resp_nopassdata = json.loads(resp_nopass.data)
        self.assertListEqual([400, 400], [resp_noname.status_code,
                                          resp_nopass.status_code])
        self.assertEqual(resp_nonamedata["message"]["username"], ("Enter"
                                                                  " Username"))
        self.assertEqual(resp_nopassdata["message"]["password"], ("Enter the"
                                                                  " password"))
