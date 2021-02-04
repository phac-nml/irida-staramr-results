from irida_api import IridaAPI

irida = IridaAPI()
analyses = irida.get_analyses_from_projects("3")
irida.analysis_to_csv("8")
