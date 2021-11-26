## todo give this file a better name

import logging
import sys

from irida_staramr_results.version import __version__
from irida_staramr_results import downloader, api, parser


def _init_api(args_dict):
    """
    Connects to IRIDA RESTful API and returns an irida_api instance.
    """
    try:
        irida_api = api.IridaAPI(
            args_dict["client_id"],
            args_dict["client_secret"],
            args_dict["base_url"],
            args_dict["username"],
            args_dict["password"])
    except api.exceptions.IridaConnectionError:
        logging.error("Unable to connect to IRIDA REST API. "
                      "Ensure your client info and account credentials are correct.")
        sys.exit(1)

    return irida_api

# todo give this function a better name
def phil_function(args_need_to_go_here):
    ## TODO: this info should be gotten from function args
    args_dict = {
        "project": 0,
        "from_date": "",
        "to_data": "",
        "client_id": "",
        "client_secret": "",
        "base_url": "",
        "username": "",
        "password": ""
    }

    # Connect to IRIDA REST API
    logging.info("Connecting to IRIDA API...")
    irida_api = _init_api(args_dict)
    logging.info("Successfully connected to IRIDA API.")

    # Start downloading results
    data_frames = downloader.download_all_results(
        irida_api, args_dict["project"], args_dict["from_date"], args_dict["to_date"])
    logging.info(f"Download complete for project id [{args_dict['project']}.")

    return data_frames

"""
from irida-staramr-results.grabber import phil_function

my_dataframe = phil_function(args_need_to_go_here)
"""