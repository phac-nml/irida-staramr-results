
SHEET_NAMES = {
    "staramr-resfinder.tsv": "ResFinder",
    "staramr-detailed-summary.tsv": "Detailed_Summary",
    "staramr-settings.txt": "Settings",
    "staramr-summary.tsv": "Summary",
    "staramr-plasmidfinder.tsv": "PlasmidFinder",
    "staramr-mlst.tsv": "MLST_Summary"
}

class AmrOutput(object):

    def __init__(self, file_json, file_txt, file_key):
        self.file_info = file_json
        self.file_content = file_txt
        self.file_key = file_key

    def get_contents(self):
        return self.file_content

    def get_file_name(self):
        return self.file_info["label"]

    def get_sheet_name(self):
        return SHEET_NAMES[self.file_key]
