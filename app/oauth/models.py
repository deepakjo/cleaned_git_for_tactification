from flask import current_app, url_for, request, flash
from flask_oauthlib.client import OAuth, OAuthException

oauth = OAuth(current_app)

class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self, **kwargs):
        """
        This function is to return the contents from provider
        :rtype: str
        """
        pass

    def authorize_response(self):
        pass

    def get_callback_url(self):
        return url_for('oauth_rt.oauth_callback', provider=self.provider_name, next=request.args.get('next'),
                       _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]

class FacebookSignIn(OAuthSignIn):

    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        credentials = current_app.config['OAUTH_CREDENTIALS']['facebook']
    
        print "id=%s key=%s" % (credentials['id'], credentials['secret'])
        self.service = oauth.remote_app(
            'facebook',
            consumer_key=credentials['id'],
            consumer_secret=credentials['secret'],
            request_token_params={'scope': 'public_profile, email'},
            base_url='https://graph.facebook.com',
            request_token_url=None,
            access_token_url='/oauth/access_token',
            access_token_method='GET',
            authorize_url='https://www.facebook.com/dialog/oauth'
        )

        self.service._tokengetter = self.get_facebook_oauth_token

    def authorize(self):
        return self.service.authorize(callback=self.get_callback_url())

    def authorize_response(self):
        resp = self.service.authorized_response()

        print 'resp', resp
        if (resp is None):
            print "Access denied: reason=%s error=%s" %(request.args['error_reason'],
                                                        request.args['error_description'])
            return None, None, None

        if (isinstance(resp, OAuthException)):
            flash('Access denied')
            return None, None, None

        self.access_token = (resp['access_token'], '')
        me = self.service.get('/me?fields=id,name,picture,email')
        print 'fb details', me.data

        return me.data['id'], me.data['name'], me.data['picture']['data']['url']

    def get_facebook_oauth_token(self):
        print 'access_token', self.access_token
        return self.access_token

class TwitterSignIn(OAuthSignIn):
	
	def __init__(self):
		"""Class for twitter oauth"""
		super(TwitterSignIn, self).__init__('twitter')
		credentials = current_app.config['OAUTH_CREDENTIALS']['twitter']
		
		self.service = oauth.remote_app(
			'twitter',
		    consumer_key=credentials['id'],
			consumer_secret=credentials['secret'],
			base_url='https://api.twitter.com/1.1/',
			request_token_url='https://api.twitter.com/oauth/request_token',
			access_token_url='https://api.twitter.com/oauth/access_token',
			authorize_url='https://api.twitter.com/oauth/authenticate')
		
		self.service._tokengetter = self.get_twitter_oauth_token
		
	def authorize(self):
		return self.service.authorize(callback=self.get_callback_url())

	def authorize_response(self):
		resp = self.service.authorized_response()

		print 'resp', resp
		if (resp is None):
			print "Access denied: reason=%s error=%s" %(request.args['error_reason'],
                                                        request.args['error_description'])
			return None, None

		if (isinstance(resp, OAuthException)):
			flash('Access denied')
			return None, None

		id = resp['user_id']
		name = resp['screen_name']
		print 'id=%s name=%s' %(id, name)
		
		self.access_token = resp['oauth_token'], resp['oauth_token_secret']
		url = "https://twitter.com/" + name + "/profile_image?size=original"

		return id, name, url

	def get_twitter_oauth_token(self):
		print 'accessing_token', self.access_token
		return self.access_token
