import unittest
from datetime import datetime
from app import create_app, db
from app.models import User, AnonymousUser, Permission, Role, Follow

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app.testing = True
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        print 'test tear_1'
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password = 'cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password = 'cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password = 'cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password = 'cat')
        u2 = User(password = 'cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_roles_and_permissions(self):
        u = User(email='fcb@gmail.com', password='fcb')
        self.assertFalse(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.FOLLOW))

    def test_is_administrator(self):
        u = User(email='fcb@gmail.com', password='fcb')
        self.assertFalse(u.can(Permission.ADMINISTER))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))

    def test_member_since_join(self):
        u = User(email='lfc@gmail.com', password = 'cat')
        db.session.add(u)
        db.session.commit()        
        self.assertTrue(datetime.utcnow() >= u.member_since)

    def test_member_last_seen(self):    
        u = User(email='fcb@gmail.com', password = 'cat')
        db.session.add(u)
        db.session.commit()
        self.assertTrue(datetime.utcnow() >= u.last_seen)
        
    def test_generate_token_and_confirm(self):
        u = User(email='fcb@gmail.com', password = 'cat')
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_follows(self):
        u1 = User(email='johnd@example.com', username='abcd', password='cat',
                  confirmed = True, via_oauth = True)
        u2 = User(email='joanjohn@example.com', username='uxyz', password='dog',
                  confirmed = True, via_oauth = True)                  
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        timestamp_before = datetime.utcnow()
        u1.follow(u2)
        db.session.add(u1)
        db.session.commit()
        timestamp_after = datetime.utcnow()
        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        self.assertTrue(u2.is_followed_by(u1))
        self.assertTrue(u1.followed.count() == 1)
        self.assertTrue(u2.followers.count() == 1)
        f = u1.followed.all()[-1]
        self.assertTrue(f.followed == u2)
        self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
        f = u2.followers.all()[-1]
        self.assertTrue(f.follower == u1)
        u1.unfollow(u2)
        db.session.add(u1)
        db.session.commit()
        self.assertTrue(u1.followed.count() == 0)
        self.assertTrue(u2.followers.count() == 0)
        self.assertTrue(Follow.query.count() == 0)
        u2.follow(u1)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        db.session.delete(u2)
        db.session.commit()
        self.assertTrue(Follow.query.count() == 0)

    def test_to_json(self):
        u1 = User(email='johnjoe@example.com', username='johnGeo', password='cat',
                  confirmed = True, via_oauth = True)
        db.session.add(u1)
        db.session.commit()
        json_user = u1.to_json()
        print 'url', json_user['url']
        expected_keys = ['url', 'username', 'member_since', 'last_seen',
                         'followed_posts', 'post_count']
        self.assertEqual(sorted(json_user.keys()), sorted(expected_keys))
        self.assertTrue('api_rt/v1.0/user/' in json_user['url'])


