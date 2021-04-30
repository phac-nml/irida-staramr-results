def by_date_range(analysis, from_timestamp, to_timestamp):
    """
    Filters list of analysis objects with attribute "createdDate".
    Returns a new list of analyses objects that were created between from_timestamp and to_timestamp
    :param analysis:
    :param from_timestamp: unix timestamp (float)
    :param to_timestamp: unix timestamp (float)
    :return:
    """

    analysis_filtered = []

    for a in analysis:
        if from_timestamp <= a["createdDate"] <= to_timestamp:
            analysis_filtered.append(a)

    return analysis_filtered
