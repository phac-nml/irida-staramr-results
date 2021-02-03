from staramr_writer import StaramrWriter
amr_write = StaramrWriter()

analyses = amr_write.get_analyses_from_projects("3")
amr_write.analysis_to_csv("8")
