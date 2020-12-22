from pkgutil import extend_path

from gordo.client.client import Client
from gordo.client.utils import influx_client_from_uri

__path__ = extend_path(__path__, __name__)
