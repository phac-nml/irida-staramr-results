import logging
import sys
import io
from pprint import pprint
import pandas as pd

from irida_staramr_results.api import exceptions


def download_all_results(irida_api, project_id, output_name):
    """
    Downloads StarAMR results from IRIDA.
    :param irida_api:
    :param project_id:
    :param output_name:
    :return:
    """
    try:
        amr_analyses = irida_api.get_amr_analysis_results(project_id)
    except exceptions.IridaConnectionError as e:
        logging.error(f"Could not connect to IRIDA. Error: {e}")
        sys.exit(1)

    except exceptions.IridaResourceError:
        error_txt = f"The given project ID doesn't exist: {project_id}. "
        logging.error(error_txt)
        sys.exit(1)

    for a in amr_analyses:
        download_result(a, irida_api, output_name)


def download_result(analysis, irida_api, output_name):

    result_files = irida_api.get_result_files(analysis)

    for files in result_files:
        _write_to_excel(files)


def _write_to_excel(file):

    file_content = str(file.get_file_content(), "utf-8")
    data = io.StringIO(file_content)

    # Filter files to read (.csv, .txt)
    logging.debug(f"Reading [{file.get_file_name()}]...")
    data_frame = pd.read_csv(data, delimiter="\t")

    logging.info(f"Writing [{file.get_file_name()}] to an excel file.")
    data_frame.to_excel(file.get_file_name())