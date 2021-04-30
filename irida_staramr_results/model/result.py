
SHEET_NAMES = {
    "staramr-resfinder.tsv": "ResFinder",
    "staramr-detailed-summary.tsv": "Detailed_Summary",
    "staramr-settings.txt": "Settings",
    "staramr-summary.tsv": "Summary",
    "staramr-plasmidfinder.tsv": "PlasmidFinder",
    "staramr-mlst.tsv": "MLST_Summary",
    "staramr-pointfinder.tsv": "PointFinder"
}


class Result(object):

    def __init__(self, file_json, file_txt, file_key):
        self.file_info = file_json
        self.file_content = file_txt
        self.file_key = file_key

    def get_contents(self):
        # convert bytes contents to string
        contents_str = str(self.file_content, 'utf-8')

        # reformat settings.txt contents to a key:value pairs.
        if "settings.txt" in self.file_info["label"]:
            settings_dict = {}
            lines = contents_str.split("\n")
            for line in lines:
                settings_row = line.split("=")
                if len(settings_row) > 1:
                    settings_dict[settings_row[0].strip()] = settings_row[1].strip()
            return settings_dict

        return contents_str

    def get_file_name(self):
        return self.file_info["label"]

    def get_sheet_name(self):
        return SHEET_NAMES[self.file_key]
