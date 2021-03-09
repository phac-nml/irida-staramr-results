from enum import Enum


class StarAmrOutput(object):
    """
    Class for storing and getting information about StarAMR results output files
    """
    def __init__(self, identifier, name, content):
        self._file_id = identifier
        self._file_name = name
        self._file_content = content

        # File type?
        # .tsv = TSV
        # .log = LOG
        # .txt = TXT
        # .json = JSON
        # .xlsx = XLSX
        # .fasta = FASTA

    def get_file_content(self):
        return self._file_content

    def get_file_name(self):
        return self._file_name

    def get_file_type(self):

        if ".tsv" in self._file_name:
            return ""
        if ".txt" in self._file_name:
        if ".json" in self._file_name:
        if ".xlsx" in self._file_name:
        if ".fasta" in self._file_name:
        if ".log" in self._file_name:

class FileType(Enum.enum):
    FASTA = 1
    JSON = 2
    LOG = 3
    TSV = 4
    TXT = 5
    XLSX = 6

