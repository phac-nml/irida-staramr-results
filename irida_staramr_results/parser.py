import yaml
import logging
import sys


def parse_config(config_file_path):
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
