import argparse
import logging
import sys

from irida_staramr_results.version import __version__
from irida_staramr_results import downloader, api, parser, validate


logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

def init_argparser():
    argument_parser = argparse.ArgumentParser(
        prog="irida-staramr-results",
        description="Exports StarAMR results available through IRIDA into a single excel report."
    )
    argument_parser.add_argument("-v", "--version", action="version", version=f"{argument_parser.prog} {__version__}",
                                 help="The current version of irida-staramr-results.")
    argument_parser.add_argument("-p", "--project", action="store", required=True, type=int,
                                 help="Required. Project(s) to scan for StarAMR results.")
    argument_parser.add_argument("-o", "--output", action="store", default="output",
                                 help="The name of the output excel file.")
    argument_parser.add_argument("-u", "--username", action="store",
                                 help="This is your IRIDA account username.")
    argument_parser.add_argument("-pw", "--password", action="store",
                                 help="This is your IRIDA account password.")
    argument_parser.add_argument("-c", "--config", action="store", required=True,
                                 help="Required. Path to a configuration file. ")
    argument_parser.add_argument("-sr", "--split_results", action="store_true",
                                 help="Export each analysis results into separate output files resulting to "
                                      "one excel file per analysis.")
    argument_parser.add_argument("-fd", "--from_date", action="store",
                                 help="Download only results of the analysis that were created FROM this date (YYYY-MM-DD).")
    argument_parser.add_argument("-td", "--to_date", action="store",
                                 help="Download only results of the analysis that were created UP UNTIL this date (YYYY-MM-DD).")


    return argument_parser


def _validate_args(args):
    """
    Validates argument input by the users and returns a dictionary of required information from arguments.
        - If user does not include username and password in arguments, the program prompts the user to enter it.
        - If user specify ".xlsx" for the output name, this method removes it.
        - Validates date arguments (from and to)
    :param args:
    :return dictionary:
    """

    user_credentials = validate.user_credentials(args.username, args.password)
    output_file_name = validate.output_file_name(args.output)
    date_range = validate.date_range(args.from_date, args.to_date)

    return {'username': user_credentials["username"],
            'password': user_credentials["password"],
            'config': args.config,
            'project': args.project,
            'output': output_file_name,
            'split_results': args.split_results,
            'from_date': date_range["from_date"],
            'to_date': date_range["to_date"]}


def _init_api(args_dict, config_dict):
    """
    Connects to IRIDA RESTful API and returns an irida_api instance.
    """
    try:
        irida_api = api.IridaAPI(
            config_dict["client_id"],
            config_dict["client_secret"],
            config_dict["base_url"],
            args_dict["username"],
            args_dict["password"])
    except api.exceptions.IridaConnectionError:
        logging.error("Unable to connect to IRIDA REST API. "
                      "Ensure your client info and account credentials are correct.")
        sys.exit(1)

    return irida_api


def main():
    """
    Main entry point of irida_staramr_results.
    Accepts commands from command line to be processed by the program.
    """
    argument_parser = init_argparser()

    args = argument_parser.parse_args()

    args_dict = _validate_args(args)

    try:
        config_dict = parser.parse_config(args_dict["config"])
    except parser.exceptions.ConfigFileNotFoundError:
        logging.error("Configuration file not found.")
        sys.exit(1)
    except parser.exceptions.ConfigInformationError:
        logging.error("An error occurred related to the information of the config file.")
        sys.exit(1)

    # Connect to IRIDA REST API
    logging.info("Connecting to IRIDA API...")
    irida_api = _init_api(args_dict, config_dict)
    logging.info("Successfully connected to IRIDA API.")

    # Start downloading results
    downloader.download_all_results(irida_api, args_dict["project"], args_dict["output"], args_dict["split_results"],
                                    args_dict["from_date"], args_dict["to_date"])


# This is called when the program is run for the first time
if __name__ == "__main__":
    main()
