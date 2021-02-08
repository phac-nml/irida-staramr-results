import sys
import argparse
from version import __version__
from irida_api import IridaAPI


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
    argument_parser.add_argument("-bs", "--base-url", action="store",
                                 help="Override 'base_url' in config file. The URL to the IRIDA server.")
    argument_parser.add_argument("-u", "--username", action="store",
                                 help="Override the 'username' in config file. This is your IRIDA account username.")
    argument_parser.add_argument("-pw", "--password", action="store",
                                 help="Override the 'password' in config file. This is your IRIDA account password.")
    argument_parser.add_argument("-ci", "--client-id", action="store",
                                 help="Override the 'client_id' field in config file. This is created and provided by IRIDA used to handle by the server.")
    argument_parser.add_argument("-cs", "--client-secret", action="store",
                                 help="Override the 'client_secret' field in config file. This is created and provided by IRIDA used to handle by the server.")


    return argument_parser

def main():

    argument_parser = init_argparser()

    if len(sys.argv) == 1:
        argument_parser.print_help()
        sys.exit(1)

    args = argument_parser.parse_args()
    args_dict = vars(args)

    if args_dict["project"] is None:
        print("Please specify project(s) to scan for results.")
    else:
        irida = IridaAPI()
        analyses = irida.get_analyses_from_projects(args_dict["project"])
        print(analyses)


# This is called when the program is run for the first time
if __name__ == "__main__":
    main()