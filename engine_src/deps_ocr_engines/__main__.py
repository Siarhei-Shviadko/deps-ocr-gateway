import logging

import click

from deps_ocr_engines.entrypoint import create_fastapi
from deps_ocr_engines.extras import Application

_logger = logging.getLogger(__name__)


@click.group()
def cli() -> None:
    pass


@click.command()
def serve() -> None:
    fastapi_app = create_fastapi()

    Application(fastapi_app, fastapi_app.app.config.gunicorn()).run()  # type: ignore


if __name__ == "__main__":
    cli.add_command(serve)
    cli()
