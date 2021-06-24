import io
import os
import logging

from datetime import datetime
import pandas as pd

from irida_staramr_results import filter, util

_directory_name = ""


def download_all_results(irida_api, project_id, output_file_name, separate_mode, from_timestamp, to_timestamp):
    """
    Main function for downloading StarAMR results to an excel file.
    :param irida_api:
    :param project_id:
    :param output_file_name:
    :param separate_mode: boolean, export file data separately if True
    :param from_timestamp: 00:00:00 of this day
    :param to_timestamp: 23:59:58 of this day
    :return:
    """

    logging.info(f"Requesting completed amr analysis submissions for project id [{project_id}]. "
                 f"This may take a while...")

    amr_completed_analysis_results = irida_api.get_completed_amr_analysis_results(project_id)

    if len(amr_completed_analysis_results) < 1:
        logging.warning(f"No completed amr analysis results type for project id [{project_id}].")
        return

    # Filter analysis created since target date (in timestamp)
    amr_completed_analysis_results = filter.by_date_range(amr_completed_analysis_results, from_timestamp, to_timestamp)

    if len(amr_completed_analysis_results) < 1:
        from_date = util.timestamp_to_local(from_timestamp)
        to_date = util.timestamp_to_local(to_timestamp - 86400000)
        logging.warning(f"No completed amr analysis submission created from [{from_date}] to [{to_date}]. Exiting..")
        return

    global _directory_name
    _directory_name = "staramr-results-" + datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    logging.info(f"Creating directory name {_directory_name} to store results files.")
    os.mkdir(_directory_name)


    if separate_mode:
        # Write the collection of files into a file, one file per analysis
        logging.info(f"Writing each results data per analysis in their separate output file...")
        for a in amr_completed_analysis_results:
            results_files = irida_api.get_analysis_result_files(a["identifier"])
            data_frames = _files_to_data_frames(results_files)
            out_name = _get_output_file_name(output_file_name, a["createdDate"])
            logging.info(f"Creating a file named {out_name}.xlsx for analysis [{a['identifier']}]. ")
            _data_frames_to_excel(data_frames, out_name)
    else:
        # Base case, collect all the data into dataframes, one per unique file name, then write a single file.
        logging.info(f"Appending all results data in one output file.")
        data_frames = {}
        for a in amr_completed_analysis_results:
            logging.info(f"Appending analysis [{a['identifier']}]. ")
            result_files = irida_api.get_analysis_result_files(a["identifier"])
            data_frames = _append_file_data_to_existing_data_frames(result_files, data_frames)
        _data_frames_to_excel(data_frames, output_file_name)

    logging.info(f"Download complete for project id [{project_id}].")


def _get_output_file_name(prefix_name, timestamp):
    """
    Generates an output file name. This method is called from the main downloader function when the mode is non-append.
        - Converts unix timestamp to UTC.
    :param prefix_name: the name added before the time.
    :param timestamp: unix timestamp in millisecond
    :return: output name as <prefix_name>-YYYY-mm-ddTHH-MM-SS.
    """

    date = datetime.utcfromtimestamp(timestamp/1000)
    date_formatted = date.strftime('%Y-%m-%dT%H-%M-%S')

    output_file_name = prefix_name + "-" + date_formatted

    # if filename already exists, add an increment number
    increment = 1
    target_path = os.path.join(_directory_name, output_file_name + ".xlsx")
    while os.path.isfile(target_path):
        output_file_name = f"{prefix_name}-{date_formatted} ({increment})"
        target_path = os.path.join(_directory_name, output_file_name + ".xlsx")
        increment = increment + 1
        logging.info(f"File name already exists, {output_file_name}.xlsx generated.")

    return output_file_name


def _data_frames_to_excel(data_frames, output_file_name):
    """
    Writes data_frames to the output file.
    Each dataframe is appended as a separate sheet.
    :param data_frames:
    :param output_file_name:
    :return:
    """

    # create new file
    target_path = f"{_directory_name}/{output_file_name}.xlsx"
    with pd.ExcelWriter(target_path, engine='xlsxwriter') as writer:
        # append data frame to file
        for file_sheet_name in data_frames:
            logging.debug(f"Writing {file_sheet_name} data to {output_file_name}.xlsx.")
            df = data_frames[file_sheet_name]
            df.to_excel(writer, sheet_name=file_sheet_name, index=False)

        # auto-fit column width
        for file_sheet_name in data_frames:
            _auto_fit_column_width(writer, data_frames[file_sheet_name], file_sheet_name)


def _auto_fit_column_width(writer, data_frame, sheet_name, max_width=75):
    """
    Auto adjust column width to fit content, with max width, in a excel file.
    :param writer:
    :param data_frame:
    :param sheet_name:
    :param max_width:
    :return:
    """
    worksheet = writer.sheets[sheet_name]
    for index, col in enumerate(data_frame):  # loop through all columns
        series = data_frame[col]

        # get maximum width of cells in that column plus extra space
        width = max((
            series.astype(str).map(len).max(),
            len(str(series.name))
        )) + 1

        if width > max_width:
            width = max_width

        worksheet.set_column(index, index, width)


def _files_to_data_frames(results_files):
    """
    Accepts a list of results files and returns them as dictionary of sheetname:dataframe pairs.
    eg. { "sheetname":{dataframe}, ..., "sheetname":{dataframe} }
    :param results_files: array of Results object
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
    :return: an updated dictionary of dataframe objects containing the newly appended data per filename.
             example: {'filename1':dataframe1, 'filename2':dataframe2, ...}
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
        data_frame = pd.DataFrame([file_content])
    else:
        data_frame = pd.read_csv(io.StringIO(file_content), delimiter="\t")

    return data_frame
