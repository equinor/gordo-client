from gordo.client.utils import parse_module_path


def test_parse_module_path():
    assert parse_module_path("gordo.client.Client") == ("gordo.client", "Client")
    assert parse_module_path("gordo.Client") == ("gordo", "Client")
    assert parse_module_path("Client") == (None, "Client")
