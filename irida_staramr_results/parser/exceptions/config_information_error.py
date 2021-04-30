class ConfigInformationError(Exception):
    """
    This error is thrown when the information of the configuration file was incorrect.
    Reasons could be:
     - a key:value was missing
     - field was spelled incorrectly

     See example-config.yml for guidance.
    """

    pass
