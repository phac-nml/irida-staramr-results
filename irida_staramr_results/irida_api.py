import json
import logging
import exceptions

from urllib.error import HTTPError
from urllib.parse import urljoin, urlparse
from rauth import OAuth2Service
from requests import ConnectionError


class IridaAPI(object):

    def __init__(self, client_id, client_secret, base_url, username, password, max_wait_time=20, http_max_retries=5):
        """
        Creates a session by connecting to IRIDA REST API via OAuth2Service with password grant type.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.username = username
        self.password = password
        self.max_wait_time = max_wait_time
        self.http_max_retries = http_max_retries

        self.access_token_url = '/oauth/token'

        self.session = None
        self._create_session()

    def _get_oauth_service(self):
        """
        Get oauth service to be used to get access token
        :return OAuthService
        """

        url = urlparse(self.base_url)

        access_token_url = urljoin(self.base_url, "api/oauth/token")
        oauth_service = OAuth2Service(
            client_id=self.client_id,
            client_secret=self.client_secret,
            name="irida",
            access_token_url=access_token_url,
            base_url= url.scheme + "://" + url.netloc
        )

        return oauth_service

    def _get_access_token(self, oauth_service):
        """
        Get access token to be used to get session from oauth_service

        :param
            oauth_service -- OAuth2Service from _get_oauth_service

        :return access token
        """

        def token_decoder(d):
            """
            Safely parse given dictionary
            :param d: returned dictionary (access token)
            :return: evaluated dictionary
            """
            try:
                irida_dict = json.loads(d.decode('utf-8'))
            except (SyntaxError, ValueError):
                # SyntaxError happens when something that looks nothing like a token is returned (ex: 404 page)
                # ValueError happens with the path returns something that looks like a token, but is invalid
                #   (ex: forgetting the /api/ part of the url)
                raise ConnectionError("Unexpected response from server, URL may be incorrect.")

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
            # TODO: Add a max retry everytime it attempts to connect. At the moment, program keep running.
            #  (Cannot detect failed connection?)
            access_token = oauth_service.get_access_token(
                decoder=token_decoder, **params)
        except ConnectionError as e:
            logging.error("Can not connect to IRIDA.")
            raise ConnectionError("Could not connect to the IRIDA server. URL may be incorrect."
                                  f"IRIDA returned with error message: {e.args}")
        except KeyError as e:
            logging.error("Can not get access token from IRIDA.")
            raise Exception("Could not get access token from IRIDA. Credentials may be incorrect. "
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

    def _get_resource(self, url, headers=None):
        """
            Grabs a resource from irida rest api with the provide FULL resource endpoint url formatted in string

            :param url: headers:
            :return a response object
        """

        if headers is None:
            headers = {"Accept": "*/*"}

        try:
            # TODO: re-validate session, in case it already expires.
            response = self.session.get(url, headers=headers)
        except Exception as e:  # should this be a connection error?
            logging.error("Failed to create a session with the IRIDA API. "
                          "Session may have been expired or connection may have failed.")
            raise exceptions.IridaConnectionError(f"No session found. Error message: {e.args}")

        # TODO: better response handler

        if response.status_code not in range(200, 299):
            raise HTTPError(url, response.status_code, "HTTPError occurred.", response.headers, None)

        return response

    def _get_link(self, target_url, target_key, target_dict=None):
        """
        Makes a call to target_url(api) expecting a json response
        Tries to retrieve target_key from response to find link to resource
        Raises exceptions if target_key not found or target_url is invalid

        :param target_url: URL to retrieve link from
        :param target_key: name of link (e.g projects or project/samples)
        :param target_dict: optional dict containing key and value to search in targets.
                            (e.g {key="identifier",value="100"} to retrieve where identifier=100)

        :return: link if it exists
        """

        logging.debug(f"irida_api._get_link: target_url: {target_url}, target_key: {target_key}.")

        response = self._get_resource(target_url)

        if target_dict:  # we are targeting specific resources in the response

            try:
                resources_list = response.json()["resource"]["resources"]
            except KeyError as e:
                # TODO: This try except block has been added to log a crash that has occurred, to find the source.
                #   This is occurring for an unknown reason.
                #   Once docs can be gathered displaying information, we can determine the source of the bug and fix it.
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
                raise exceptions.IridaKeyError(target_dict["key"] + " not found. Available keys: "
                                                                    ", ".join(resources_list[0].keys()))

            except StopIteration:
                raise exceptions.IridaKeyError(target_dict["value"] + " not found.")

        else:
            links_list = response.json()["resource"]["links"]

        try:
            ret_val = next(link["href"] for link in links_list
                           if link["rel"] == target_key)
        except StopIteration:
            error_txt = target_key + " not found in links. Available links: " + \
                        ", ".join([str(link["rel"]) for link in links_list])
            logging.debug(error_txt)
            raise exceptions.IridaKeyError(error_txt)

        return ret_val

    def get_amr_analysis_results(self, project_id):
        """
        Get all AMR detection analysis results from a project id.
        If no analysis results found in the project, it returns an empty array.
        :param project_id:
        :return analysis_result_list:
        """

        try:
            project_analysis_submissions = self._get_analysis_submissions_from_projects(project_id)
        except KeyError:
            error_txt = f"The given project ID doesn't exist: {project_id}. "
            raise exceptions.IridaKeyError(error_txt)

        all_analysis_results = self._get_all_analysis_results(project_analysis_submissions)

        # Filter AMR Detection results
        amr_analysis_results = [analysis_result for analysis_result in all_analysis_results if
                                self._is_type_amr(analysis_result)]

        return amr_analysis_results

    def _get_analysis_submissions_from_projects(self, project_id):
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

        response = self._get_resource(analysis_submissions_url)
        analysis_submissions = response.json()["resource"]["resources"]

        return analysis_submissions

    def _get_all_analysis_results(self, project_analysis_submissions):

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
                analysis_result = self._get_resource(analysis_results_url).json()["resource"]
                analysis_result_list.append(analysis_result)

        return analysis_result_list

    def _is_type_amr(self, analysis_result):
        """
        Checks if the analysis result is an amr detection type.
        :param analysis_result:
        :return boolean:
        """
        return analysis_result["analysisType"]["type"] == "AMR_DETECTION"
