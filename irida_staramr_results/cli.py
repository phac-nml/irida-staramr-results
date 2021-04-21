import argparse
import getpass
import logging
import sys
import time
from datetime import datetime, timezone

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
    argument_parser.add_argument("-o", "--output", action="store", default="output",
                                 help="The name of the output excel file.")
    argument_parser.add_argument("-u", "--username", action="store",
                                 help="This is your IRIDA account username.")
    argument_parser.add_argument("-pw", "--password", action="store",
                                 help="This is your IRIDA account password.")
    argument_parser.add_argument("-c", "--config", action="store", required=True,
                                 help="Required. Path to a configuration file. ")
    argument_parser.add_argument("-a", "--append", action="store_true",
                                 help="Append all analysis results to a single output file.")
    argument_parser.add_argument("--fromDate", action="store",
                                 help="Download only results of the analysis that were created FROM this date.")
    argument_parser.add_argument("--toDate", action="store",
                                 help="Download only results of the analysis that were created UP UNTIL this date.")


    return argument_parser


def _validate_args(args):
    """
    Validates argument input by the users and returns a dictionary of required information from arguments.
        - If user does not include username and password in arguments, the program prompts the user to enter it.
        - If user specify ".xlsx" for the output name, this method removes it.
        - Converts date (in UTC) to unix timestamp. If not specified, it will be set to 0
    :param args:
    :return dictionary:
    """
    if args.username is None:
        args.username = input("Enter your IRIDA username: \n")
    if args.password is None:
        print("Enter your IRIDA password: ")
        args.password = getpass.getpass()
    if args.output.endswith(".xlsx"):
        args.output = args.output[:-len(".xlsx")]

    date = _validate_date(args.fromDate, args.toDate)

    return {'username': args.username,
            'password': args.password,
            'config': args.config,
            'project': args.project,
            'output': args.output,
            'append': args.append,
            'fromDate': date["fromDate"],
            'toDate': date["toDate"]}


def _validate_date(from_date, to_date):
    """
    Sets up FROM and TO date values in unix timestamp.
    :param from_date:
    :param to_date:
    :return:
    """

    if from_date is None:
        from_date = 0
    else:
        from_date = local_to_timestamp(from_date)

    if to_date is None:
        to_date = time.time() * 1000
    else:
        to_date = local_to_timestamp(to_date)

    if (to_date > time.time() * 1000) or (from_date > time.time() * 1000):
        logging.error("DateError: --fromDate and --toDate cannot be in the future.")
        sys.exit(1)

    if from_date > to_date:
        logging.error("DateError: --fromDate must be earlier than --toDate.")
        sys.exit(1)


    return {"fromDate": from_date, "toDate": to_date}


def local_to_timestamp(target_date):
    """
    Converts date in local time to unix timestamp in milliseconds. Assumes "YYYY-mm-dd" is the input date format.
    :param target_date: string type formatted as YYYY-mm-dd
    :return:
    """

    dt = datetime.strptime(target_date, "%Y-%m-%d")  # local
    dt_utc = dt.replace(tzinfo=timezone.utc)  # local -> utc
    timestamp = dt_utc.timestamp() * 1000  # utc -> unix timestamp (millisecond)

    return timestamp


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
    amr_downloader.download_all_results(irida_api, args_dict["project"], args_dict["output"], args_dict["append"],
                                        args_dict["fromDate"], args_dict["toDate"])


# This is called when the program is run for the first time
if __name__ == "__main__":
    main()
