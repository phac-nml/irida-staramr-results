from rauth import OAuth2Service
from requests import ConnectionError
import json
import logging


def token_decoder(s):
    return json.loads(s.decode('utf-8'))


class IridaAPI(object):

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = 'http://10.10.50.155:8080'
        self.username = 'admin'
        self.password = 'Test123!'

        # self.max_wait_time = max_wait_time
        # self.http_max_retries = http_max_retries

        self.base_endpoint = '/api'
        self.access_token_url = '/oauth/token'


        self.session = None
        self._create_session()

    def _get_oauth_service(self):
        """
        get oauth service to be used to get access token

        :return OAuthService
        """

        access_token_url = self.base_url + self.base_endpoint + self.access_token_url

        oauth_service = OAuth2Service(
            client_id=self.client_id,
            client_secret=self.client_secret,
            name="irida",
            access_token_url=access_token_url,
            base_url=self.base_url
        )

        return oauth_service

    def _get_access_token(self, oauth_service):
        """
        Get access token to be used to get session from oauth_service

        :param
            oauth_service -- OAuth2Service from _get_oauth_service

        :return access token
        """

        params = {
            "data": {
                "grant_type": "password",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "username": self.username,
                "password": self.password
            }
        }

        try:
            access_token = oauth_service.get_access_token(
                decoder=token_decoder, **params)
        except ConnectionError as e:
            # logging.error("Can not connect to IRIDA")
            raise Exception("Could not connect to the IRIDA server. URL may be incorrect."
                            f"IRIDA returned with error message: {e.args}")
        except KeyError as e:
            # logging.error("Can not get access token from IRIDA")
            raise Exception("Could not get access token from IRIDA. Credentials may be incorrect."
                            f"IRIDA returned with error message: {e.args}")

        return access_token

    def _create_session(self):
        """
        Creates oauth2session with oauth_service and access token.

        :return: oauth2session object
        """

        oauth_service = self._get_oauth_service()
        access_token = self._get_access_token(oauth_service)
        session = oauth_service.get_session(access_token)

        self.session = session

    def get_resource(self, resource_endpoint):
        """
            Grabs a resource from irida rest api with the provide resource endpoint url formatted in string

            :param resource_endpoint
            :return a response object
        """

        endpoint = self.base_url + self.base_endpoint + resource_endpoint

        # TODO: allow any Accept type
        headers = {
            "Accept": "text/plain"
        }

        try:
            response = self.session.get(endpoint, headers=headers)
        except Exception as e:
            raise Exception(f"No session found. Error message: {e.args}")

        # TODO: better response handler

        if response.status_code not in range(200, 299):
            raise Exception("Invalid request.")

        return response
