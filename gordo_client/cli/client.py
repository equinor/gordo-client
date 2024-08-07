"""Gordo-client click command."""

import json
import logging
import os
import pickle  # noqa:S403
import sys
from copy import copy
from datetime import datetime
from pprint import pprint
from typing import Iterable, List, Optional, Tuple, Union
from typing.io import IO

import click
import pandas as pd
import simplejson
import yaml
from gordo_core.data_providers import providers
from requests import Session

from gordo_client import Client, __version__
from gordo_client.cli.custom_types import DataProviderParam, IsoFormatDateTime, key_value_par
from gordo_client.forwarders import ForwardPredictionsIntoInflux


@click.group("client")
@click.version_option(version=__version__, prog_name="gordo-client")
@click.option("--project", help="The project to target")
@click.option("--host", help="The host the server is running on", default="localhost")
@click.option("--port", help="Port the server is running on", default=443)
@click.option("--scheme", help="tcp/http/https", default="https")
@click.option("--batch-size", help="How many samples to send", default=100000)
@click.option("--parallelism", help="Maximum asynchronous jobs to run", default=10)
@click.option(
    "--metadata",
    type=key_value_par,
    multiple=True,
    default=(),
    help="Key-Value pair to be entered as metadata labels, may use this option multiple times. "
    + "to be separated by a comma. ie: --metadata key,val --metadata some key,some value",
)
@click.option(
    "--session-config",
    type=yaml.safe_load,
    default="{}",  # noqa:P103
    help="Config json/yaml to set on the requests.Session object. Useful when needing to supply"
    + "authentication parameters such as header keys. ie. --session-config {'headers': {'API-KEY': 'foo-bar'}}",
)
@click.option("--log-level", type=str, help="Run client with custom log-level.", envvar="GORDO_LOG_LEVEL")
@click.option(
    "--all-columns",
    is_flag=True,
    default=False,
    help="Return all columns for prediction. Including 'smooth-..' columns",
)
@click.pass_context
def gordo_client(ctx: click.Context, *args, session_config=None, **kwargs):
    """Entry sub-command for client related activities."""
    log_level = ctx.params.get("log_level")
    if log_level:
        logging.basicConfig(
            level=logging.getLevelName(log_level),
            format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        )

    kwargs = copy(kwargs)
    if session_config:
        session = Session()
        for key, value in session_config.items():
            setattr(session, key, value)
        kwargs["session"] = session
    kwargs.pop("log_level", None)

    ctx.obj = {"args": args, "kwargs": kwargs}


@click.command("predict")
@click.argument("start", type=IsoFormatDateTime())
@click.argument("end", type=IsoFormatDateTime())
@click.option(
    "--target",
    help="A list of machines to target. If not provided then target all machines in the project",
    default=[],
    multiple=True,
)
@click.option(
    "--data-provider",
    type=DataProviderParam(),
    envvar="DATA_PROVIDER",
    help="DataProvider dict encoded as json. Must contain a 'type' key with the name of a DataProvider as value.",
)
@click.option("--output-dir", type=click.Path(exists=True), help="Save output prediction dataframes in a directory")
@click.option("--influx-uri", help="Format: <username>:<password>@<host>:<port>/<optional-path>/<db_name>")
@click.option("--influx-api-key", help="Key to provide to the destination influx")
@click.option("--influx-recreate-db", help="Recreate the desintation DB before writing", is_flag=True, default=False)
@click.option("--forward-resampled-sensors", help="forward the resampled sensor values", is_flag=True, default=False)
@click.option("--n-retries", help="Time client should retry failed predictions", type=int, default=5)
@click.option(
    "--parquet/--no-parquet", help="Use parquet serialization when sending and receiving data from server", default=True
)
@click.pass_context
def predict(
    ctx: click.Context,
    start: datetime,
    end: datetime,
    target: List[str],
    data_provider: providers.GordoBaseDataProvider,
    output_dir: str,
    influx_uri: str,
    influx_api_key: str,
    influx_recreate_db: bool,
    forward_resampled_sensors: bool,
    n_retries: int,
    parquet: bool,
):
    """Run some predictions against the target."""
    if influx_uri is None:
        prediction_forwarder = None
    else:
        prediction_forwarder = ForwardPredictionsIntoInflux(
            destination_influx_uri=influx_uri,
            destination_influx_api_key=influx_api_key,
            destination_influx_recreate=influx_recreate_db,
            n_retries=n_retries,
        )

    ctx.obj["kwargs"].update(
        {
            "data_provider": data_provider,
            "forward_resampled_sensors": forward_resampled_sensors,
            "n_retries": n_retries,
            "use_parquet": parquet,
            "prediction_forwarder": prediction_forwarder,
        }
    )

    client = Client(*ctx.obj["args"], **ctx.obj["kwargs"])

    # Fire off getting predictions
    predictions = client.predict(start, end, targets=target)  # type: Iterable[Tuple[str, pd.DataFrame, List[str]]]

    # Loop over all error messages for each result and log them
    click.secho(f"\n{'-' * 20} Summary of failed predictions (if any) {'-' * 20}")
    exit_code = 0
    for _name, _df, error_messages in predictions:
        for err_msg in error_messages:
            # Any error message indicates we encountered at least one error
            exit_code = 1
            click.secho(err_msg, fg="red")

    # Shall we write the predictions out?
    if output_dir is not None:
        for name, prediction_df, _err_msgs in predictions:
            prediction_df.to_csv(os.path.join(output_dir, f"{name}.csv.gz"), compression="gzip")
    sys.exit(exit_code)


@click.command("metadata")
@click.option("--output-file", type=click.File(mode="w"), help="Optional output file to save metadata")
@click.option(
    "--target",
    help="A list of machines to target. If not provided then target all machines in the project",
    default=[],
    multiple=True,
)
@click.pass_context
def metadata(ctx: click.Context, output_file: Optional[IO[str]], target: List[str]):
    """Get metadata from a given endpoint."""
    client = Client(*ctx.obj["args"], **ctx.obj["kwargs"])
    target_metadata = {
        k: v.dict()  # type: ignore
        for k, v in client.get_metadata(targets=target).items()  # type: ignore
    }
    if output_file:
        json.dump(target_metadata, output_file)
        click.secho(f"Saved metadata json to file: '{output_file}'")
    else:
        pprint(target_metadata)
    return target_metadata


@click.command("download-model")
@click.argument("output-dir", type=click.Path(exists=True))
@click.option(
    "--target",
    help="A list of machines to target. If not provided then target all machines in the project",
    default=[],
    multiple=True,
)
@click.pass_context
def download_model(ctx: click.Context, output_dir: str, target: List[str]):
    """Download the actual model from the target and write to an output directory."""
    client = Client(*ctx.obj["args"], **ctx.obj["kwargs"])
    models = client.download_model(targets=target)

    # Iterate over mapping of models and save into their own sub dirs of the output_dir
    for model_name, model in models.items():
        model_out_dir = os.path.join(output_dir, model_name)
        os.mkdir(model_out_dir)
        click.secho(f"Writing model '{model_name}' to directory: '{model_out_dir}'...", nl=False)
        _dump_model(model, model_out_dir)
        click.secho("done")

    click.secho(f"Wrote all models to directory: {output_dir}", fg="green")


def _dump_model(obj: object, dest_dir: Union[os.PathLike, str], model_metadata: Optional[dict] = None):
    with open(os.path.join(dest_dir, "model.pkl"), "wb") as m:
        pickle.dump(obj, m)
    if model_metadata is not None:
        with open(os.path.join(dest_dir, "metadata.json"), "w") as f:
            simplejson.dump(model_metadata, f, default=str)


gordo_client.add_command(predict)
gordo_client.add_command(metadata)
gordo_client.add_command(download_model)
