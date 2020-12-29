"""Custom click types."""
import os
import typing

import click
import yaml
from dateutil import parser
from gordo_dataset.data_provider import providers


class DataProviderParam(click.ParamType):
    """Load a DataProvider from JSON/YAML representation or from a JSON/YAML file."""

    name = "data-provider"

    def convert(self, value, param, ctx):
        """Convert the value for data provider."""
        if os.path.isfile(value):
            with open(value) as f:
                kwargs = yaml.safe_load(f)
        else:
            kwargs = yaml.safe_load(value)

        if "type" not in kwargs:
            self.fail("Cannot create DataProvider without 'type' key defined")

        kind = kwargs.pop("type")

        provider_class = getattr(providers, kind, None)
        if provider_class is None:
            self.fail(f"No DataProvider named '{kind}'")
        return provider_class(**kwargs)


class IsoFormatDateTime(click.ParamType):
    """Parse a string into an ISO formatted datetime object."""

    name = "iso-datetime"

    def convert(self, value, param, ctx):
        """Convert the value for iso date."""
        try:
            return parser.isoparse(value)
        except ValueError:
            self.fail(f"Failed to parse date '{value}' as ISO formatted date'")


def key_value_par(val) -> typing.Tuple[str, str]:
    """Split input of 'key,val'."""
    return val.split(",")
