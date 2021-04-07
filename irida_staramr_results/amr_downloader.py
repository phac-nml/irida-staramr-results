import io
import os
import logging

import pandas as pd


def download_all_results(irida_api, project_id, output_file_name, mode_append):
    """
    Main function for downloading StarAMR results to an excel file.
    :param irida_api:
    :param project_id:
    :param output_file_name:
    :param mode_append: boolean, appends all file data together when True
    :return:
    """

    logging.info(f"Requesting completed amr analysis submissions for project id [{project_id}]. "
                 f"This may take a while...")
    amr_completed_analysis_submissions = irida_api.get_amr_analysis_submissions(project_id)

    if len(amr_completed_analysis_submissions) < 1:
        logging.warning(f"No completed amr analysis submission type for project id [{project_id}].")

    if mode_append:
        # In append mode, collect all the data into dataframes, one per unique file name, then write a single file.
        data_frames = {}
        for a in amr_completed_analysis_submissions:
            result_files = irida_api.get_analysis_result_files(a["identifier"])
            data_frames = _append_file_data_to_existing_data_frames(result_files, data_frames)
        _write_data_frames_to_excel(data_frames, output_file_name)
    else:
        # Base case, write the collection of files into a file, one file per analysis
        for a in amr_completed_analysis_submissions:
            result_files = irida_api.get_analysis_result_files(a["identifier"])
            data_frames = _files_to_data_frames(result_files)
            _write_data_frames_to_excel(data_frames, output_file_name)

    logging.info(f"Download complete for project id [{project_id}].")


def _write_data_frames_to_excel(data_frames, output_file_name):
    """
    Writes data_frames to the output file.
    Each dataframe is appended as a separate sheet.
    :param data_frames:
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
        for file_sheet_name in data_frames:
            logging.info(f"Appending {file_sheet_name} data to {output_file_name}.")
            data_frames[file_sheet_name].to_excel(writer, sheet_name=file_sheet_name, index=False)


def _files_to_data_frames(results_files):
    """
    Accepts a list of results files and returns them as dictionary of filename:dataframe key:value pairs
    :param results_files:
    :return:
    """
    data_frames = {}
    for file in results_files:
        data_frames[file.get_sheet_name()] = _convert_to_df(file.get_contents())

    return data_frames


def _append_file_data_to_existing_data_frames(results_files, data_frames):
    """
    Accepts a list of results files and appends the data to a given list of data_frames.
    The data_frames can be an empty dict
    :param results_files: a list of files to be converted into dataframes, and added or appended to the data_frames dict
    :param data_frames: a dictionary of filename:dataframe pairs
    :return: list of dataframe objects with data from input appended, one per unique file name
    """

    for file in results_files:
        file_sheet_name = file.get_sheet_name()
        if file_sheet_name not in data_frames.keys():
            # new file, new dataframe
            data_frames[file_sheet_name] = _convert_to_df(file.get_contents())
        else:
            # appending data to existing dataframe
            prev_data = data_frames[file_sheet_name]
            curr_data = _convert_to_df(file.get_contents())
            updated_data = prev_data.append(curr_data)
            data_frames[file_sheet_name] = updated_data

    return data_frames


def _convert_to_df(file_content):
    """
    Converts dictionary or tsv contents to a data frame
    :param file_content:
    :return data_frame:
    """
    if type(file_content) is dict:
        data = list(file_content.items())
        data_frame = pd.DataFrame(data, columns=["Key", "Value"])
    else:
        data_frame = pd.read_csv(io.StringIO(file_content), delimiter="\t")

    return data_frame

