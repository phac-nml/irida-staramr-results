import argparse
import getpass
import logging
import sys

from irida_staramr_results.version import __version__
from irida_staramr_results import amr_downloader, api, parsers


logging.basicConfig(level=logging.INFO)


def init_argparser():
    argument_parser = argparse.ArgumentParser(
        prog="irida-staramr-results",
        description="Exports StarAMR results available through IRIDA into a single excel report."
    )
    argument_parser.add_argument("-v", "--version", action="version", version=f"{argument_parser.prog} {__version__}",
                                 help="The current version of irida-staramr-results.")
    argument_parser.add_argument("-p", "--project", action="store", required=True, type=int,
                                 help="Required. Project(s) to scan for StarAMR results.")
    argument_parser.add_argument("-o", "--output", action="store", default="out.xlsx",
                                 help="The name of the output excel file.")
    argument_parser.add_argument("-u", "--username", action="store",
                                 help="This is your IRIDA account username.")
    argument_parser.add_argument("-pw", "--password", action="store",
                                 help="This is your IRIDA account password.")
    argument_parser.add_argument("-c", "--config", action='store', required=True,
                                 help='Required. Path to a configuration file. ')
    argument_parser.add_argument("-a", "--append", action='store_true',
                                 help="Append all analysis results to a single output file.")

    return argument_parser


def _validate_args(args):
    """
    Validates argument input by the users and returns a dictionary of required information from arguments.
    If user does not include username and password in arguments,
    the program prompts the user to enter it.
    :param args:
    :return dictionary:
    """
    if args.username is None:
        args.username = input("Enter your IRIDA username: \n")
    if args.password is None:
        print("Enter your IRIDA password: ")
        args.password = getpass.getpass()

    return {'username': args.username,
            'password': args.password,
            'config': args.config,
            'project': args.project,
            'output': args.output,
            'append': args.append}


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
        config_dict = parsers.parse_config(args_dict["config"])
    except parsers.exceptions.ConfigFileNotFoundError:
        logging.error("Configuration file not found.")
        sys.exit(1)
    except parsers.exceptions.ConfigInformationError:
        logging.error("An error occurred related to the information of the config file.")
        sys.exit(1)

    # Connect to IRIDA REST API
    logging.info("Connecting to IRIDA API...")
    irida_api = _init_api(args_dict, config_dict)
    logging.info("Successfully connected to IRIDA API.")

    # Start downloading results
    amr_downloader.download_all_results(irida_api, args_dict["project"], args_dict["output"], args_dict["append"])


# This is called when the program is run for the first time
if __name__ == "__main__":
    main()
