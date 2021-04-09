import yaml
import logging

from irida_staramr_results import parsers


def parse_config(config_file_path):
    """
    Parse configuration YAML file provided by the user.
    :param config_file_path:
    :return config_dict:
    """

    try:
        with open(config_file_path, "r") as file:
            config_info = yaml.load(file, Loader=yaml.FullLoader)
    except FileNotFoundError:
        logging.error(f"No configuration file found in {config_file_path}.")
        raise parsers.exceptions.ConfigFileNotFoundError()

    try:
        config_dict = {"base_url": config_info["base-url"],
                       "client_id": config_info["client-id"],
                       "client_secret": config_info["client-secret"]}
    except KeyError as key:
        logging.error(f"No key {key} exists in config file."
                      f"Ensure your client information in the configuration file is correct.")
        raise parsers.exceptions.ConfigInformationError()

    return config_dict
