#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# __author__ = 'ames0k0'


if __name__ != "__main__":
    exit()


import argparse

from core.main import MyReadingManga


parser = argparse.ArgumentParser(
    epilog="""
    --url https://myreadingmanga.info/.../ --keep-images .
    """
)
parser.add_argument(
    "--url",
    help="Manga URL to download",
    type=str,
)
parser.add_argument(
    "--download-chapters",
    help="Flag to download manga chapters, default is False",
    type=bool,
    default=False,
)
parser.add_argument(
    "--keep-images",
    help="Flag to keep downloaded manga images, default is False",
    type=bool,
    default=False,
)
args = parser.parse_args()


if not args.url:
    parser.print_help()
    exit(0)


mrm = MyReadingManga(
    url=args.m,
    download_all_chapters=args.download_chapters,
    keep_downloaded_images=args.keep_images,
)
