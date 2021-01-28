from rauth import OAuth2Service
import json


def decode_access_token(s):
    return json.loads(s.decode('utf-8'))


class IridaAPI(object):
    name = 'irida'
    grant_type = 'password'
    scope = 'read'
    username = 'admin'
    password = 'Test123!'
    client_id = None
    client_secret = None
    base_url = 'http://10.10.50.155:8080'
    endpoint_path = base_url + '/api'
    access_token_url = '/oauth/token'

    access_token = None
    session = None

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def _perform_auth(self):

        oauth_service = OAuth2Service(
            client_id=self.client_id,
            client_secret=self.client_secret,
            name=self.name,
            access_token_url=self.endpoint_path + self.access_token_url,
            base_url=self.base_url)

        params = {'data': {
            'grant_type': self.grant_type,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'username': self.username,
            'password': self.password}
        }

        self.access_token = oauth_service.get_access_token(decoder=decode_access_token, **params)
        self.session = oauth_service.get_session(self.access_token)

    def get_resource(self, resource_endpoint):

        self._perform_auth()
        response = self.session.get(self.endpoint_path + resource_endpoint, headers={'Accept': 'text/plain'})

        # TODO better response handler

        if response.status_code not in range(200, 299):
            raise Exception("Invalid request.")

        return response
