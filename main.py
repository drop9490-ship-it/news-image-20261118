#!/usr/bin/env python3
"""Entry program for make.fun news-image-20261118.

Copies the rendered front page (entry.png, shipped in this repository) to
the output directory. Standard library only, no network, no fonts, no
timestamps: both runs write the same bytes.
"""

import os
import shutil


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    shutil.copyfile(os.path.join(here, "entry.png"),
                    os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
