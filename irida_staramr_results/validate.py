import sys
import logging
import getpass
import time

from irida_staramr_results import util


def user_credentials(username, password):
    if username is None:
        username = input("Enter your IRIDA username: \n")
    if password is None:
        print("Enter your IRIDA password: ")
        password = getpass.getpass()

    return {"username": username,
            "password": password}


def output_file_name(file_name):
    if file_name.endswith(".xlsx"):
        file_name = file_name[:-len(".xlsx")]

    return file_name


def date_range(from_date, to_date):
    """
    Sets up FROM and TO date values in unix timestamp.
    :param from_date:
    :param to_date:
    :return:
    """

    if from_date is None:
        from_date = 0
    else:
        from_date = util.local_to_timestamp(from_date)

    if to_date is None:
        to_date = time.time() * 1000
    else:
        to_date = util.local_to_timestamp(to_date)

    if (to_date > time.time() * 1000) or (from_date > time.time() * 1000):
        logging.error("DateError: --from_date and --to_date cannot be in the future.")
        sys.exit(1)

    if from_date > to_date:
        logging.error("DateError: --from_date must be earlier than --to_date.")
        sys.exit(1)

    # Add 24 hours (86400000 milliseconds) to include to_date's full day.
    to_date = to_date + 86400000


    return {"from_date": from_date, "to_date": to_date}
