import sys
import argparse
import logging
from version import __version__
from irida_api import IridaAPI
from urllib.error import HTTPError


def init_argparser():
    argument_parser = argparse.ArgumentParser(
        prog="irida-staramr-results",
        description="Exports StarAMR results available through IRIDA into a single excel report."
    )
    argument_parser.add_argument("-v", "--version", action="version", version=f"{argument_parser.prog} {__version__}",
                                 help="The current version of irida-staramr-results.")
    argument_parser.add_argument("-p", "--project", action="store",
                                 help="Project(s) to scan for StarAMR results.")
    argument_parser.add_argument("-o", "--output", action="store",
                                 help="The name of the output excel file.")

    # Arguments that will override fields in the config file.
    argument_parser.add_argument("-u", "--username", action="store",
                                 help="This is your IRIDA account username.")
    argument_parser.add_argument("-pw", "--password", action="store",
                                 help="This is your IRIDA account password.")

    return argument_parser


def main():
    """
    Main entry point of irida_staramr_results.
    Accepts commands form terminal to be processed by the program.
    """
    argument_parser = init_argparser()

    if len(sys.argv) == 1:
        argument_parser.print_help()
        sys.exit(1)

    args = argument_parser.parse_args()
    args_dict = vars(args)

    if args_dict["project"] is None:
        logging.error("Please specify project(s) to scan for results.")
        sys.exit(1)

    irida = IridaAPI("neptune", "6KlqQOEzEy55GBrQdIa28DE9wFk7Y9RkDRmYfCCUKR", "http://10.10.50.155:8080", "admin",
                     "Test123!")

    try:
        analyses = irida.get_analyses_from_projects(args_dict["project"])

    # TODO: better exception handler
    except ConnectionError as e:
        error_txt = f"Could not connect to IRIDA. Error: {e}"
        raise Exception(error_txt)
    except HTTPError as e:
        project_id = args_dict["project"]
        error_txt = f"The given project ID doesn't exist: {project_id}. "
        logging.error(error_txt)
        raise Exception(error_txt + f"Error: {e}")
    except Exception as e:
        error_txt = f"An Error has occurred. Error: {e}"
        logging.error(error_txt)
        raise Exception(error_txt)


# This is called when the program is run for the first time
if __name__ == "__main__":
    main()
