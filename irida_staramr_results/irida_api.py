import ast
import logging
import threading
from http import HTTPStatus
from urllib.error import URLError
from urllib.parse import urljoin, urlparse
from rauth import OAuth2Service
from requests import ConnectionError
from requests.adapters import HTTPAdapter

from . import exceptions

# For a truly independent api module, we should have a signal, or pubsub system in the module, that the progress module
# can subscribe to. That way, the api module is seperate, and other applications could use the emits/messages in their
# own setups.


class IridaAPI(object):

    def __init__(self, client_id, client_secret,
                 base_url, username, password, max_wait_time=20, http_max_retries=5):
        """
        Create OAuth2Session and store it

        arguments:
            client_id -- client_id for creating access token.
            client_secret -- client_secret for creating access token.
            base_url -- url of the IRIDA server
            username -- username for server
            password -- password for given username

        return ApiCalls object
        """

        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.username = username
        self.password = password
        self.max_wait_time = max_wait_time
        self.http_max_retries = http_max_retries

        self._session_lock = threading.Lock()
        self._session_set_externally = False
        self._create_session()
        self.cached_projects = None
        self.cached_samples = {}

        # these two are used when sending signals to the progress module
        self._current_upload_project_id = None
        self._current_upload_sample_name = None

    @property
    def _session(self):
        try:  # Todo: rework this code without the try/catch/finally and odd exception raise
            self._session_lock.acquire()
            response = self._session_instance.options(self.base_url)
            if response.status_code != HTTPStatus.OK:
                raise Exception
            else:
                logging.debug("Existing session still works, going to reuse it.")
        except Exception:
            logging.debug("Token is probably expired, going to get a new session.")
            self._reinitialize_session()
        finally:
            self._session_lock.release()

        return self._session_instance

    def _reinitialize_session(self):
        oauth_service = self._get_oauth_service()
        access_token = self._get_access_token(oauth_service)
        _sess = oauth_service.get_session(access_token)
        # We add a HTTPAdapter with max retries so we don't fail out if one request gets lost
        _sess.mount('https://', HTTPAdapter(max_retries=self.http_max_retries))
        _sess.mount('http://', HTTPAdapter(max_retries=self.http_max_retries))
        self._session_instance = _sess

    def _create_session(self):
        """
        create session to be re-used until expiry for get and post calls

        returns session (OAuth2Session object)
        """

        def validate_url_form(url):
            """
                offline 'validation' of url. parse through url and see if its malformed
            """
            parsed = urlparse(url)
            valid = len(parsed.scheme) > 0
            return valid

        if self.base_url[-1:] != "/":
            self.base_url = self.base_url + "/"
        if not validate_url_form(self.base_url):
            logging.error("Cannot create session. {} is not a valid URL".format(self.base_url))
            raise exceptions.IridaConnectionError("Cannot create session." + self.base_url + " is not a valid URL")

        self._reinitialize_session()

    def _get_oauth_service(self):
        """
        get oauth service to be used to get access token

        returns oauthService
        """

        access_token_url = urljoin(self.base_url, "oauth/token")
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
        get access token to be used to get session from oauth_service

        arguments:
            oauth_service -- O2AuthService from get_oauth_service

        returns access token
        """

        def token_decoder(return_dict):
            """
            safely parse given dictionary

            arguments:
                return_dict -- access token dictionary

            returns evaluated dictionary
            """
            # It is supposedly safer to decode bytes to string and then use ast.literal_eval than just use eval()
            try:
                irida_dict = ast.literal_eval(return_dict.decode("utf-8"))
            except (SyntaxError, ValueError):
                # SyntaxError happens when something that looks nothing like a token is returned (ex: 404 page)
                # ValueError happens with the path returns something that looks like a token, but is invalid
                #   (ex: forgetting the /api/ part of the url)
                raise ConnectionError("Unexpected response from server, URL may be incorrect")
            return irida_dict

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
            logging.error("Can not connect to IRIDA")
            raise exceptions.IridaConnectionError("Could not connect to the IRIDA server. URL may be incorrect."
                                                  " IRIDA returned with error message: {}".format(e.args))
        except KeyError as e:
            logging.error("Can not get access token from IRIDA")
            raise exceptions.IridaConnectionError("Could not get access token from IRIDA. Credentials may be incorrect."
                                                  " IRIDA returned with error message: {}".format(e.args))

        return access_token

    def _validate_url_existence(self, url):
        """
        tries to validate existence of given url by trying to open it.
        true if HTTP OK and no errors when authenticating credentials
        if errors or non HTTP.OK code occur, throws a IridaConnectionError

        arguments:
            url -- the url link to open and validate

        returns
            true if http response OK 200
            raises IridaConnectionError otherwise
        """
        try:
            response = self._session.get(url)
        except URLError as e:
            logging.error("Could not connect to IRIDA, URL '{}' responded with: {}"
                          "".format(url, str(e)))
            raise exceptions.IridaConnectionError("Could not connect to IRIDA, URL '{}' responded with: {}"
                                                  "".format(url, str(e)))
        except Exception as e:
            logging.error("Could not connect to IRIDA, non URLError Exception occurred. URL '{}' Error: {}"
                          "".format(url, str(e)))
            raise exceptions.IridaConnectionError("Could not connect to IRIDA, non URLError Exception occurred. "
                                                  "URL '{}' Error: {}".format(url, str(e)))

        if response.status_code == HTTPStatus.OK:
            return True
        else:
            logging.error("Could not connect to IRIDA, URL '{}' responded with: {} {}"
                          "".format(url, response.status_code, response.reason))
            raise exceptions.IridaConnectionError("Could not connect to IRIDA, URL '{}' responded with: {} {}"
                                                  "".format(url, response.status_code, response.reason))

    def _get_link(self, target_url, target_key, target_dict=None):
        """
        makes a call to target_url(api) expecting a json response
        tries to retrieve target_key from response to find link to resource
        raises exceptions if target_key not found or target_url is invalid

        arguments:
            target_url -- URL to retrieve link from
            target_key -- name of link (e.g projects or project/samples)
            target_dict -- optional dict containing key and value to search
                in targets.
            (e.g {key="identifier",value="100"} to retrieve where
                identifier=100)

        returns link if it exists
        """

        logging.debug("irida_api._get_link: target_url: {}, target_key: {}".format(target_url, target_key))

        self._validate_url_existence(target_url)
        response = self._session.get(target_url)

        if target_dict:  # we are targeting specific resources in the response

            # TODO: This try except block has been added to log a crash that has occurred, to find the source.
            try:
                resources_list = response.json()["resource"]["resources"]
            except KeyError as e:
                # This is occurring for an unknown reason.
                # Once docs can be gathered displaying information, we can determine the source of the bug and fix it.
                logging.error("Dumping json response from IRIDA:")
                logging.error(str(response.json()))
                logging.error("Dumping python KeyError:")
                logging.error(e)
                error_txt = "Response from IRIDA Could not be parsed. Please show the log to your IRIDA Administrator."
                logging.error(error_txt)
                raise exceptions.IridaKeyError(error_txt)
            # try to get all keys from target_dict to our list or links
            try:
                links_list = next(
                    r["links"] for r in resources_list
                    if r[target_dict["key"]].lower() == str(target_dict["value"]).lower()
                )

            except KeyError:
                raise exceptions.IridaKeyError(
                    target_dict["key"] + " not found. Available keys: " ", ".join(resources_list[0].keys()))

            except StopIteration:
                raise exceptions.IridaKeyError(target_dict["value"] + " not found.")

        else:  # get all the links in the response
            links_list = response.json()["resource"]["links"]
        try:
            ret_val = next(link["href"] for link in links_list
                           if link["rel"] == target_key)

        except StopIteration:
            logging.debug(target_key + " not found in links. Available links: "
                                       ", ".join([str(link["rel"]) for link in links_list]))
            raise exceptions.IridaKeyError(target_key + " not found in links. Available links: "
                                                        ", ".join([str(link["rel"]) for link in links_list]))

        return ret_val

    def get_amr_analysis_results(self, project_id):
        """
        Get all AMR detection analysis results from a project id.
        If no analysis results found in the project, it returns an empty array.
        :param project_id:
        :return analysis_result_list:
        """
        try:
            # Get all analysis results in project
            all_analysis_results = self._get_all_analysis_results(project_id)
        except KeyError:
            error_txt = f"The given project ID doesn't exist: {project_id}. "
            raise exceptions.IridaResourceError(error_txt)

        # Filter AMR Detection results
        amr_analysis_results = [analysis_result for analysis_result in all_analysis_results if
                                self._is_type_amr(analysis_result)]

        return amr_analysis_results

    def _get_analysis_submissions(self, project_id):
        """
        Returns an array of all analyses for a given project
        :param project_id:
        :return project_analysis_list:
        """
        try:
            project_url = self._get_link(self.base_url, "projects")
            analysis_submissions_url = self._get_link(project_url, "project/analyses",
                                                      target_dict={
                                                          "key": "identifier",
                                                          "value": project_id
                                                      })
        except StopIteration:
            logging.error(f"The given project ID doesn't exist: {project_id}")
            raise exceptions.IridaResourceError("The given project ID doesn't exist", project_id)

        response = self._session.get(analysis_submissions_url)
        analysis_submissions = response.json()["resource"]["resources"]

        return analysis_submissions

    def _get_all_analysis_results(self, project_id):

        try:
            project_analysis_submissions = self._get_analysis_submissions(project_id)
        except KeyError:
            error_txt = f"The given project ID doesn't exist: {project_id}. "
            raise exceptions.IridaResourceError(error_txt)

        analysis_result_list = []

        for analysis_submission in project_analysis_submissions:

            analysis_submission_id = analysis_submission["identifier"]

            try:
                analysis_submission_url = self._get_link(self.base_url, "analysisSubmissions")
                analysis_results_url = self._get_link(analysis_submission_url, "analysis",
                                                      target_dict={
                                                          "key": "identifier",
                                                          "value": analysis_submission_id
                                                      })
            except exceptions.IridaKeyError:
                """
                Catches an exception if an analysis submission does not contain an analysis result.
                Ignores the exception and continue with searching the rest of analysis submissions
                """
                logging.info(
                    f"No analysis result exists for analysis submission id [{analysis_submission_id}]. Skipping...")
                continue
            else:
                analysis_result = self._session.get(analysis_results_url).json()["resource"]
                analysis_result_list.append(analysis_result)

        return analysis_result_list

    def _is_type_amr(self, analysis_result):
        """
        Checks if the analysis result is an amr detection type.
        :param analysis_result:
        :return boolean:
        """
        return analysis_result["analysisType"]["type"] == "AMR_DETECTION"
