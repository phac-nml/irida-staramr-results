from io import StringIO
import pandas as pd
from irida_api import IridaAPI


class StaramrWriter(object):

    def __init__(self):
        self.irida_api = IridaAPI("neptune", "6KlqQOEzEy55GBrQdIa28DE9wFk7Y9RkDRmYfCCUKR")

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
        return self.irida_api.get_resource_from_path(f"/projects/{_id}")

    def get_analyses_from_projects(self, _id):
        """
        Returns an array containing analysis objects for a given project

        :param _id:
        :return project_analysis_list:
        """
        project_analysis_list = []

        project = self.get_project_from_id(_id).json()

        project_analyses_url = self._get_href_from_links("project/analyses", project["resource"]["links"])

        if  project_analyses_url is None:
            print("No 'project/analyses' link relation in project object.")
        else:
            project_analysis = {} # analysis object

            project_analyses_response = self.irida_api.get_resource(project_analyses_url).json()

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

        analysis = self.irida_api.get_resource_from_path(f"/analysisSubmissions/{analysis_id}/analysis").json()

        # grabs file link from analysisSubmission endpoint and uses that file link to grab file data.
        for fn in file_names:
            file_resource_link = self._get_href_from_links(f"outputFile/{fn}.tsv", analysis["resource"]["links"])

            # TODO: include settings.txt
            if file_resource_link is None:
                print(f"No file name {fn}.tsv exist.")
            else:
                file = self.irida_api.get_resource(file_resource_link, headers={"Accept": "text/plain"})
                s = str(file.content, 'utf-8')
                data = StringIO(s)
                df = pd.read_csv(data, delimiter="\t")
                df.to_csv(f"out/{fn}.csv")


