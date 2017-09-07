import re
import unittest
from flask import url_for
from app import create_app, db
from app.models import User, Role, Post

def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app.testing = True
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get(url_for('main.index'))
        self.assertTrue('SIGN IN' in response.get_data(as_text=True))

    def test_register_and_login(self):
        # register a new account
        response = self.client.post(url_for('auth.register'), data={
            'email': 'john@example.com',
            'username': 'john',
            'password': 'cat',
            'password2': 'cat',
            'profile_pic': '/home/deepak/blog_for_grunt/profile_picture/fcb_1.jpg'
        })
        self.assertTrue(response.status_code == 200)

        # login with the new account
        response = self.client.post(url_for('auth.login'), data={
            'email': 'john@example.com',
            'password': 'cat'
        }, follow_redirects=True)
        self.assertTrue(
            b'You have not confirmed your account yet' in response.data)

        # send a confirmation token
        user = User.query.filter_by(email='john@example.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get(url_for('auth.confirm', token=token),
                                   follow_redirects=True)
        self.assertTrue(
            b'You have confirmed your account' in response.data)

        # log out
        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        self.assertTrue(b'SIGN IN' in response.data)
    
    def test_add_post(self):
        response = self.client.post(url_for('auth.register'), data=dict(
            email= 'deepak_p_jose@yahoo.co.in',
            username= 'admin',
            password= 'cat',
            password2= 'cat',
            profile_pic= '/home/deepak/blog_for_grunt/profile_picture/fcb_1.jpg'
        ))
        print 'register resp', response
        self.assertTrue(response.status_code == 200)

        response = self.client.post(url_for('auth.login'), data=dict(
            email= 'deepak_p_jose@yahoo.co.in',
            password= 'cat'
        ), follow_redirects=True)
        print 'login_response', response.data
        self.assertTrue(
            b'You have not confirmed your account yet' in response.data)

        # send a confirmation token
        user = User.query.filter_by(email='john@example.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get(url_for('auth.confirm', token=token),
                                   follow_redirects=True)
        self.assertTrue(
            b'You have confirmed your account' in response.data)
            
        print 'Response', response.data
        self.assertTrue(
            b'SIGN OUT' in response.data)

        post_response = self.client.post(url_for('main.index'),
                                         data = {'tactical_gif': '/home/deepak/blog_for_grunt/gifs/ft-bayern-borrussia_2.gif',
                                                 'header': 'Bayern Vs Borussia',
                                                 'body': 'This is a picture from the era of Jurgen Klopp'
                                                })
        self.assertTrue(b'Bayern Vs Borussia' in response.data)
