import ast
import logging
import threading
from http import HTTPStatus
from urllib.error import URLError
from urllib.parse import urljoin, urlparse

from requests import ConnectionError
from requests.adapters import HTTPAdapter
from rauth import OAuth2Service

from irida_staramr_results.api import exceptions
from irida_staramr_results.model.result import Result


# For a truly independent api module, we should have a signal, or pubsub system in the module, that the progress module
# can subscribe to. That way, the api module is separate, and other applications could use the emits/messages in their
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

        self.analysis_submission_url = None
        self.project_url = None
        self.target_submission_ids = {}  # { result_id : submission_id }

        self._session_lock = threading.Lock()
        self._session_set_externally = False
        self._create_session()
        self.cached_projects = None
        self.cached_samples = {}

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

    def _is_result_type_amr(self, analysis_result):
        """
        Checks if the analysis result is an amr detection type.
        This function is used in `get_completed_amr_analysis_results()`
        :param analysis_result: a dictionary of an analysis results with keys `analysisType` and `type`
        :return boolean:
        """
        return analysis_result["analysisType"]["type"] == "AMR_DETECTION"

    def _is_submission_type_amr(self, analysis_submission):
        """
        Returns true if the analysis result of the submission is type amr.
            1. Checks if the analysis submission is completed.
            2. Gets the analysis results and check its type.
        This function is used in get_amr_analysis_submissions().
        :param analysis_submission:
        :return:
        """

        if analysis_submission["analysisState"] == "COMPLETED":
            # If an analysis state of the submission is COMPLETED,
            # we can retrieve its analysis results and find out its type.
            analysis_result = self._get_analysis_result(analysis_submission["identifier"])
            return self._is_result_type_amr(analysis_result)

        return False

    def get_completed_amr_analysis_results(self, project_id):
        """
        Get COMPLETED analysis results of AMR DETECTION type from a project id.
        If no analysis results found in the project, it returns an empty array.
        :param project_id: integer
        :return completed_amr_analysis_results: an array of completed amr analysis result dictionaries
        """

        completed_amr_analysis_results = []

        try:
            logging.info(f"Requesting project [{project_id}]'s analysis submissions.")
            project_analysis_submissions = self._get_project_analysis_submissions(project_id)
        except KeyError:
            error_txt = f"The given project ID doesn't exist: {project_id}. "
            raise exceptions.IridaResourceError(error_txt)

        # Filter Completed AMR Detection type
        for analysis_submission in project_analysis_submissions:
            if analysis_submission["analysisState"] == "COMPLETED":
                analysis_result = self._get_analysis_result(analysis_submission["identifier"])
                if self._is_result_type_amr(analysis_result):
                    completed_amr_analysis_results.append(analysis_result)

                    # cache submission id with corresponding result id
                    self._store_submission_id(analysis_result["identifier"], analysis_submission["identifier"])

        if len(completed_amr_analysis_results) < 1:
            logging.warning(f"No Completed AMR Detection type found in project [{project_id}].")

        return completed_amr_analysis_results

    def _get_project_analysis_submissions(self, project_id):
        """
        Returns an array of ALL analysis submissions (regardless of the type) for a given project
        :param project_id: integer
        :return analysis_submissions: array
        """
        if not self.project_url:
            self.project_url = self._get_link(self.base_url, "projects")

        try:
            logging.info(f"Requesting {self.project_url}.")
            project_analysis_submissions_url = self._get_link(self.project_url, "project/analyses",
                                                      target_dict={
                                                          "key": "identifier",
                                                          "value": project_id
                                                      })
        except StopIteration:
            logging.error(f"The given project ID doesn't exist: {project_id}")
            raise exceptions.IridaResourceError("The given project ID doesn't exist", project_id)

        response = self._session.get(project_analysis_submissions_url)
        analysis_submissions = response.json()["resource"]["resources"]

        return analysis_submissions

    def _get_analysis_result(self, analysis_submission_id):
        """
        Returns an analysis result json object based on the analysis submission id.
        Note: Not all analysis submissions will be COMPLETED, thus, not all will have analysis results.
            It will return an empty object if no results exists.
        :param analysis_submission_id:
        :return analysis_result:
        """

        if not self.analysis_submission_url:
            logging.info("Requesting analysis submissions url.")
            self.analysis_submission_url = self._get_link(self.base_url, "analysisSubmissions")

        analysis_results_url = self.get_analysis_results_url(analysis_submission_id)

        logging.info(f"Requesting {analysis_results_url}.")
        try:

            analysis_result = self._session.get(analysis_results_url).json()["resource"]

        except exceptions.IridaKeyError:
            """
            Catches an exception if an analysis submission does not contain an analysis result.
            It will handle it by returning an empty dictionary
            """
            logging.info(f"No analysis result exists for analysis submission id "
                         f"[{analysis_submission_id}]. Moving on...")
            analysis_result = {}

        return analysis_result

    def get_analysis_result_files(self, analysis_id):
        """
        Returns a list of Result, which are file objects, given analysis id.
        Each AMR analysis should have at least five Result file objects. staramr-pointfinder.tsv is optional.
        This function accepts analysis_id with COMPLETED analysis status and an AMR_DETECTION type,
            otherwise, it will thrown an exception.
        :param analysis_id:
        :return result_files: an array of Results object
        """

        file_list = [
            "staramr-resfinder.tsv",
            "staramr-detailed-summary.tsv",
            "staramr-settings.txt",
            "staramr-summary.tsv",
            "staramr-plasmidfinder.tsv",
            "staramr-mlst.tsv",
            "staramr-pointfinder.tsv"
        ]

        result_files = []

        # get file urls base on file_list
        for file_key in file_list:
            try:
                file_url = self._get_file_url(analysis_id, file_key)
            except exceptions.IridaKeyError:

                if file_key == "staramr-pointfinder.tsv":
                    """
                    We want ignore the IridaKeyError thrown and skip to the next iteration because PointFinder can be 
                    disabled in an amr analysis run.
                    This means the analysis does not contain the staramr-pointfinder.tsv file which is acceptable.
                    """
                    logging.debug(f"No staramr-pointfinder.tsv found as one of the output files for analysis "
                                  f"[{analysis_id}], skipping...")
                    continue
                else:
                    """
                    Catches an exception if an analysis submission does not contain an analysis result.
                    For our case, this shouldn't happen since we use analysis_id with COMPLETED analysis status and 
                    an AMR_DETECTION type given by the caller (downloader).
                    """
                    logging.error(f"No analysis result exists for analysis id "
                                  f"[{analysis_id}]. Check analysis id [{analysis_id}] "
                                  f"and ensure the analysis status is COMPLETED and with type AMR_DETECTION.")

            # response containing json
            response_json = self._session.get(file_url)

            # response containing text (actual file contents)
            response_txt = self._session.get(file_url, headers={"Accept": "text/plain"})

            # create output object
            output = Result(file_json=response_json.json()["resource"],
                            file_txt=response_txt.content,
                            file_key=file_key)
            result_files.append(output)

        return result_files

    def _get_file_url(self, analysis_id, file_key):
        """
        Returns a URL of a file given an file key (file name with extension)
        :param analysis_id: integer
        :param file_key: string, file name (eg. staramr-resfinder.tsv)
        :return file_url: string
        """
        if not self.analysis_submission_url:
            self.analysis_submission_url = self._get_link(self.base_url, "analysisSubmissions")

        analysis_result_url = self.get_analysis_results_url(self.target_submission_ids[analysis_id])

        file_url = self._get_link(analysis_result_url, "outputFile/" + file_key)
        return file_url

    def get_analysis_results_url(self, analysis_submission_id):
        """
        This method returns analysis results url given the analysis submission id.
        Note: self._get_link() is not used here to lessen the amount of api calls made.
        A drawback, this method assumes the endpoint is /analysisSubmissions/{submission_id}/analysis.
        But the benefits of improved efficiency outweighs the drawback.
        :param analysis_submission_id:
        :return analysis results url: string
        """
        if not self.analysis_submission_url:
            logging.info("Requesting analysis submissions url.")
            self.analysis_submission_url = self._get_link(self.base_url, "analysisSubmissions")

        return f"{self.analysis_submission_url}/{analysis_submission_id}/analysis"

    def _store_submission_id(self, results_id, submission_id):
        """
        This method stores results id and submission id to a dictionary declared as an instance variable called
        target_submission_ids. eg. { results_id:submission_id, ... }
        :param results_id: the id of analysis results corresponding to the analysis submission given.
        :param submission_id: analysis submission id
        :return None:
        """
        self.target_submission_ids[results_id] = submission_id
