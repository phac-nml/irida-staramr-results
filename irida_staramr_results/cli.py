import argparse
import getpass
import logging
import sys

import yaml

from irida_staramr_results.version import __version__
from irida_staramr_results import amr_downloader
from irida_staramr_results.api import exceptions, IridaAPI

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
            'output': args.output}


def _parse_config(config_file_path):
    """
    Parse configuration YAML file provided by the user.
    It assumes the file name to be "example-config.yml".
    :param config_file_path:
    :return config_dict:
    """

    try:
        with open(config_file_path, "r") as file:
            config_info = yaml.load(file, Loader=yaml.FullLoader)
    except FileNotFoundError as e:
        logging.error(f"No configuration file found in {config_file_path}.")
        sys.exit(1)

    try:
        config_dict = {"base_url": config_info["base-url"],
                       "client_id": config_info["client-id"],
                       "client_secret": config_info["client-secret"]}
    except KeyError as key:
        logging.error(f"No key {key} exists in config file."
                      f"Ensure your client information in the configuration file is correct.")
        sys.exit(1)
    except TypeError as e:
        print(e)
        logging.error(f"Ensure your client information in the configuration file is formatted correctly. "
                      f"See example-config.yml for guidance.")
        sys.exit(1)

    return config_dict


def _init_api(args_dict, config_dict):
    """
    Connects to IRIDA RESTful API and returns an irida_api instance.
    """
    try:
        irida_api = IridaAPI(
            config_dict["client_id"],
            config_dict["client_secret"],
            config_dict["base_url"],
            args_dict["username"],
            args_dict["password"])
    except exceptions.IridaConnectionError:
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

    config_dict = _parse_config(args_dict["config"])

    # Connect to IRIDA REST API
    irida_api = _init_api(args_dict, config_dict)

    # Start downloading results
    amr_downloader.download_all_results(irida_api, args_dict["project"], args_dict["output"])


# This is called when the program is run for the first time
if __name__ == "__main__":
    main()
