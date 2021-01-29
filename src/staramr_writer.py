from io import StringIO
import pandas as pd
from pprint import pprint

from pandas import DataFrame

from irida_api import IridaAPI


class StaramrWriter(object):

    def __init__(self):
        self.irida_api = IridaAPI("neptune", "6KlqQOEzEy55GBrQdIa28DE9wFk7Y9RkDRmYfCCUKR")
        self.df_all = DataFrame()

    def _get_href_from_links(self, rel, links):
        for l in links:
            if l["rel"] == rel:
                return l["href"]
        return None

    def get_all_analysis_results(self, analysis_id):
        """
        Grabs all analysis results from irida and outputs all of it into one csv file.
        :param analysis_id:
        :return: analysis_csv
        """
        file_names = ["staramr-mlst.tsv",
                      "staramr-resfinder.tsv",
                      "rgi-summary.tsv",
                      "staramr-detailed-summary.tsv",
                      "staramr-summary.tsv"]

        analysis = self.irida_api.get_resource_from_path(f"/analysisSubmissions/{analysis_id}/analysis").json()

        # grabs file link from analysisSubmission endpoint ans uses that file link to grab file data.
        for fn in file_names:
            file_resource_link = self._get_href_from_links(f"outputFile/{fn}", analysis["resource"]["links"])

            if file_resource_link is None:
                print(f"No file name {fn} exist.")
            else:

                file = self.irida_api.get_resource(file_resource_link, headers={"Accept": "text/plain"})
                s = str(file.content, 'utf-8')
                data = StringIO(s)
                df = pd.read_csv(data, delimiter="\t")

                # join to dataframe
                self.df_all = pd.concat([self.df_all, df])

        # dumps dataframe contents to one csv file
        self.df_all.to_csv("out/all.csv")
