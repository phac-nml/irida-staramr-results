
SHEET_NAMES = {
    "staramr-resfinder.tsv": "ResFinder",
    "staramr-detailed-summary.tsv": "Detailed_Summary",
    "staramr-settings.txt": "Settings",
    "staramr-summary.tsv": "Summary",
    "staramr-plasmidfinder.tsv": "PlasmidFinder",
    "staramr-mlst.tsv": "MLST_Summary",
    "staramr-excel.xlsx": "PointFinder"
}


class Result(object):

    def __init__(self, file_json, file_txt, file_key):
        self.file_info = file_json
        self.file_content = file_txt
        self.file_key = file_key

    def get_contents(self):
        # Excel files do not need to be converted to utf-8 strings
        # Pointfinder data is ripped from excel file as tsv file for pointfinder is not included
        if self.file_key == "staramr-excel.xlsx":
            # return raw excel file data
            return self.file_content

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
