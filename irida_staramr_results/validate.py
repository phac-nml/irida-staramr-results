import sys
import logging
import getpass
import time

from irida_staramr_results import util


def user_credentials(username, password):
    """
    Validates username and password inputted as arguments.
    If either of the two are not specified the user will be prompted.
    :param username: username of the IRIDA account
    :param password: password of the IRIDA account
    """
    if username is None:
        username = input("Enter your IRIDA username: \n")
    if password is None:
        print("Enter your IRIDA password: ")
        password = getpass.getpass()

    return {"username": username,
            "password": password}


def output_file_name(file_name):
    """
    Validates name of the output file.
    This expects only the name without the file extension. However, if specified, it will remove it.
    :param file_name: name of output file
    """
    if file_name.endswith(".xlsx"):
        file_name = file_name[:-len(".xlsx")]

    return file_name


def date_range(from_date, to_date):
    """
    Sets up FROM and TO date values in unix timestamp (millisecond).
    :param from_date:
    :param to_date:
    :return:
    """

    if from_date is None:
        from_date = 0  # if from_date is not specified as an argument, value will be the epoch time (1 January 1970 UTC)
    else:
        from_date = util.local_to_timestamp(from_date)

    if to_date is None:
        to_date = time.time() * 1000  # if to_date is not specified as an argument, value is the current timestamp
    else:
        to_date = util.local_to_timestamp(to_date)

    # Ensure neither of the two are in the future.
    if (to_date > time.time() * 1000) or (from_date > time.time() * 1000):
        logging.error("DateError: --from_date and --to_date cannot be in the future.")
        sys.exit(1)

    # Ensure FROM is earlier than TO.
    if from_date > to_date:
        logging.error("DateError: --from_date must be earlier than --to_date.")
        sys.exit(1)

    # Add 24 hours (86400000 milliseconds) to include to_date's full day.
    to_date = to_date + 86400000


    return {"from_date": from_date, "to_date": to_date}
