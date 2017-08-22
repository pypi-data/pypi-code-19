# coding=utf-8
import pandas as pd


def search_api(query, client, date_column=[]):
    """
    Performs a query in the platform and returns the results as a dataframe [1]_.

    Parameters
    ----------
    query : json
        MQL query in JSON format
    client : SmartObjectsClient
        An instance of the SmartObjectsClient
    date_column : array_like, optional
        A list of columns to be transformed from string to datetime

    Returns
    -------
    results_dataframe : dataframe
        A dataframe with the query results

    References
    ----------
    .. [1] mnubo SmartObjects Python client
       https://github.com/mnubo/smartobjects-python-client

    Examples
    --------
    >>> from smartobjects import SmartObjectsClient
    >>> hostname = 'https://rest.sandbox.mnubo.com'
    >>> client_id = "..."
    >>> client_secret = "..."
    >>> mnubo_client = SmartObjectsClient(client_id, client_secret, hostname)
    >>> query = {"from": "event","select": [{"count": "*"}]}
    >>> df_query = mdspy.smartobjects.search_api(query, mnubo_client)
        COUNT(*)
    0  126056211
    """

    response = client.search.search(query).raw
    df_search = pd.io.json.json_normalize(response, 'rows')
    if len(response['rows']) == 0:
        return []
    df_search.columns = [col['label'] for col in response['columns']]
    for column in date_column:
        df_search[column] = pd.to_datetime(df_search[column])
    return df_search
