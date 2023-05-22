from collections import namedtuple
from typing import Dict, Optional, Tuple, Union

from influxdb import DataFrameClient, InfluxDBClient

# Prediction result representation, name=str, predictions=dataframe, error_messages=List[str]
PredictionResult = namedtuple("PredictionResult", "name predictions error_messages")


def _parse_influx_uri(uri: str) -> Tuple[str, str, str, str, str, str]:
    """
    Parse an influx URI.

    Parameters
    ----------
    uri
        Format: ``<username>:<password>@<host>:<port>/<optional-path>/<db_name>``

    Returns
    -------
        username, password, host, port, path, database
    """
    username, password, host, port, *path, db_name = uri.replace("/", ":").replace("@", ":").split(":")
    path_str = "/".join(path) if path else ""
    return username, password, host, port, path_str, db_name


def influx_client_from_uri(
    uri: str,
    api_key: Optional[str] = None,
    api_key_header: Optional[str] = "Ocp-Apim-Subscription-Key",
    recreate: bool = False,
    dataframe_client: bool = False,
    proxies: Dict[str, str] = {"https": "", "http": ""},
) -> Union[InfluxDBClient, DataFrameClient]:
    """
    Get a ``InfluxDBClient`` or ``DataFrameClient`` from a ``SqlAlchemy`` like URI.

    .. todo::
        Remove this function. Use :class:`gordo_core.utils.influx_client_from_uri` instead.

    Parameters
    ----------
    uri
        Connection string format: ``<username>:<password>@<host>:<port>/<optional-path>/<db_name>``
    api_key
        Any api key required for the client connection
    api_key_header
        The name of the header the api key should be assigned
    recreate
        Re/create the database named in the URI
    dataframe_client
        Return ``DataFrameClient`` instead of a standard ``InfluxDBClient``
    proxies
        A mapping of any proxies to pass to the influx client
    """
    username, password, host, port, path, db_name = _parse_influx_uri(uri)

    Client = DataFrameClient if dataframe_client else InfluxDBClient

    client = Client(
        host=host,
        port=port,
        database=db_name,
        username=username,
        password=password,
        path=path,
        ssl=bool(api_key),
        proxies=proxies,
    )
    if api_key:
        client._headers[api_key_header] = api_key
    if recreate:
        client.drop_database(db_name)
        client.create_database(db_name)
    return client


def parse_module_path(module_path) -> Tuple[Optional[str], str]:
    module_paths = module_path.split(".")
    if len(module_paths) == 1:
        return None, module_paths[0]
    else:
        return ".".join(module_paths[:-1]), module_paths[-1]
