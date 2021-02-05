from rauth import OAuth2Service
from requests import ConnectionError
import json
from io import StringIO
import pandas as pd


class IridaAPI(object):

    def __init__(self):
        """
        Creates a session by connecting to IRIDA REST API via OAuth2Service with password grant type.
        """
        self.client_id = "neptune"
        self.client_secret = "6KlqQOEzEy55GBrQdIa28DE9wFk7Y9RkDRmYfCCUKR"
        self.base_url = 'http://10.10.50.155:8080'
        self.username = 'admin'
        self.password = 'Test123!'

        self.base_endpoint = '/api'
        self.access_token_url = '/oauth/token'


        self.session = None
        self._create_session()

    def _token_decoder(self, s):
        return json.loads(s.decode('utf-8'))

    def _get_oauth_service(self):
        """
        Get oauth service to be used to get access token

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
                decoder=self._token_decoder, **params)
        except ConnectionError as e:
            raise Exception("Could not connect to the IRIDA server. URL may be incorrect."
                            f"IRIDA returned with error message: {e.args}")
        except KeyError as e:
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

    def _get_resource_from_path(self, endpoint_path):
        endpoint_url = self.base_url + self.base_endpoint + endpoint_path
        return self._get_resource(endpoint_url)

    def _get_resource(self, endpoint_url, headers=None):
        """
            Grabs a resource from irida rest api with the provide FULL resource endpoint url formatted in string

            :param endpoint_url: headers:
            :return a response object
        """

        if headers is None:
            headers = {"Accept": "*/*"}

        try:
            response = self.session.get(endpoint_url, headers=headers)
        except Exception as e:
            raise Exception(f"No session found. Error message: {e.args}")

        # TODO: better response handler

        if response.status_code not in range(200, 299):
            raise Exception(f"Invalid request. Status code: {response.status_code}")

        return response

    def _get_href_from_links(self, rel, links):
        """
        Returns a link based on the link relation (rel) from a list of links.

        :param rel: link relation
        :param links:
        :return: href:
        """
        for l in links:
            if l["rel"] == rel:
                return l["href"]
        return None

    def get_project_from_id(self, _id):
        """ Returns a project resource object from an id of a project """
        return self._get_resource_from_path(f"/projects/{_id}")

    def get_analyses_from_projects(self, _id):
        """
        Returns an array containing analysis objects for a given project

        :param _id:
        :return project_analysis_list:
        """
        project_analysis_list = []

        project = self.get_project_from_id(_id).json()

        project_analyses_url = self._get_href_from_links("project/analyses", project["resource"]["links"])

        if project_analyses_url is None:
            print("No 'project/analyses' link relation in project object.")
        else:
            project_analysis = {}  # analysis object

            project_analyses_response = self._get_resource(project_analyses_url).json()

            # check if resources array is not empty
            if len(project_analyses_response["resource"]["resources"]) <= 0:
                print("No analysis in this project")
            else:
                for analysis in project_analyses_response["resource"]["resources"]:

                    # create the analysis object, overrides existing information if it exists.
                    project_analysis["name"] = analysis["name"]
                    project_analysis["identifier"] = analysis["identifier"]
                    project_analysis["workflow_id"] = analysis["workflowId"]
                    project_analysis["links"] = analysis["links"]

                    # add to the list of analysis, by deep copy
                    project_analysis_list.append(project_analysis.copy())

        return project_analysis_list

    def analysis_to_csv(self, analysis_id):
        """
        Grabs all analysis results from irida and outputs all of it into one csv file.
        :param analysis_id:
        """
        file_names = ["staramr-mlst",
                      "staramr-resfinder",
                      "staramr-plasmidfinder",
                      "staramr-detailed-summary",
                      "staramr-summary"]

        analysis = self._get_analysis(analysis_id).json()

        # grabs file link from analysisSubmission endpoint and uses that file link to grab file data.
        for fn in file_names:
            file_resource_link = self._get_href_from_links(f"outputFile/{fn}.tsv", analysis["resource"]["links"])

            # TODO: include settings.txt
            if file_resource_link is None:
                print(f"No file name {fn}.tsv exist.")
            else:
                file = self._get_resource(file_resource_link, headers={"Accept": "text/plain"})
                s = str(file.content, 'utf-8')
                data = StringIO(s)
                df = pd.read_csv(data, delimiter="\t")
                df.to_csv(f"out/{fn}.csv")

    def _get_analysis(self, analysis_id):
        return self._get_resource_from_path(f"/analysisSubmissions/{analysis_id}/analysis")
