import io
import os
import logging

import pandas as pd


def download_all_results(irida_api, project_id, output_file_name):
    """
    Main function for downloading StarAMR results to an excel file.
    :param irida_api:
    :param project_id:
    :param output_file_name:
    :return:
    """

    logging.info(f"Requesting completed amr analysis submissions for project id [{project_id}]")
    amr_completed_analysis_submissions = irida_api.get_amr_analysis_submissions(project_id)

    if len(amr_completed_analysis_submissions) < 1:
        logging.warning(f"No completed amr analysis submission type for project id [{project_id}].")

    for a in amr_completed_analysis_submissions:
        result_files = irida_api.get_analysis_result_files(a["identifier"])
        _write_to_excel(result_files, output_file_name)

    logging.info(f"Download complete for project id [{project_id}].")


def _write_to_excel(result_files, output_file_name):
    """
    Converts file contents to dataframe and writes it to the output file.
    Each dataframe is appended as a separate sheet.
    :param result_files:
    :param output_file_name:
    :return:
    """

    # delete existing file if exist
    if os.path.isfile(output_file_name):
        logging.info(f"Removing existing {output_file_name}.")
        os.remove(output_file_name)

    # create new file
    logging.info(f"Creating a new file {output_file_name}.")
    with pd.ExcelWriter(output_file_name, engine='xlsxwriter') as writer:
        # append data frame to file
        for file in result_files:
            file_content = file.get_contents()
            file_sheet_name = file.get_sheet_name()

            logging.info(f"Appending {file_sheet_name} data to {output_file_name}.")
            data_frame = pd.read_csv(io.StringIO(str(file_content, 'utf-8')), delimiter="\t")
            data_frame.to_excel(writer, sheet_name=file_sheet_name)
