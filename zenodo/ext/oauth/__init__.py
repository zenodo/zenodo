import os
from flask_oauthlib.client import OAuth

oauth = OAuth()

def setup_app(app):
    # Get GitHub keys from environment variables
    app.config.setdefault('ZENODO_GITHUB_CLIENT_ID', '')
    app.config.setdefault('ZENODO_GITHUB_CLIENT_SECRET', '')

    CLIENT_ID = app.config['ZENODO_GITHUB_CLIENT_ID']
    CLIENT_SECRET = app.config['ZENODO_GITHUB_CLIENT_SECRET']
    ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
    AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    OAUTH_SCOPE = {"scope": "user:email,admin:repo_hook"}

    oauth.init_app(app)

    # Initialize an OAuth host
    oauth.remote_app(
        'github',
        consumer_key = CLIENT_ID,
        consumer_secret = CLIENT_SECRET,
        request_token_params = OAUTH_SCOPE,
        base_url='https://api.github.com/',
        request_token_url = None,
        access_token_url = ACCESS_TOKEN_URL,
        authorize_url = AUTHORIZE_URL
    )