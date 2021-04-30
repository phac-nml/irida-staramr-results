class ConfigFileNotFoundError(Exception):
    """
    This error is thrown when config file was not provided.
    Either the user did not create a config file (must be a YAML file), or
    the path provided to the config file was incorrect.
    """

    pass
