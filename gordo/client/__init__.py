from pkgutil import extend_path

from pkg_resources import get_distribution

from gordo.client.client import Client
from gordo.client.utils import influx_client_from_uri

__version__ = get_distribution("gordo.client").version

# Denote a package as a namespace package.
# https://www.python.org/dev/peps/pep-0420/#namespace-packages-today
__path__ = extend_path(__path__, __name__)
