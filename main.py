"""Entrypoint: copy entry.png into the grading output directory."""

from os import environ
from pathlib import Path
from shutil import copyfile

FILENAME = "entry.png"
DEFAULT_OUT = "/output"


def run() -> None:
    destination = Path(environ.get("MAKEFUN_OUTPUT_DIR", DEFAULT_OUT))
    destination.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).resolve().parent / FILENAME
    copyfile(source, destination / FILENAME)


if __name__ == '__main__':
    run()
