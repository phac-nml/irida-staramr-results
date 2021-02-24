import logging
import sys
import exceptions


def download_results(irida_api, project_id, output_name):
    """
    Downloads StarAMR results from IRIDA.
    :param irida_api:
    :param project_id:
    :param output_name:
    :return:
    """
    try:
        amr_analyses = irida_api.get_amr_analysis_results(project_id)
    except exceptions.IridaConnectionError as e:
        logging.error(f"Could not connect to IRIDA. Error: {e}")
        sys.exit(1)

    except exceptions.IridaResourceError as e:
        error_txt = f"The given project ID doesn't exist: {project_id}. "
        logging.error(error_txt)
        sys.exit(1)

    # TODO: on a separate PR, create a function that writes analysis to an excel file.
    # _write_to_excel(amr_analyses, output_name)

"""
Future functionality:
    _write_to_excel(amr_analyses, output_name): writes analyses to an excel file
"""
