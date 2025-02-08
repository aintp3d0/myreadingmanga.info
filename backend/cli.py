if __name__ != "__main__":
    exit()


import argparse

from core.main import MangaDownloader


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
    "--keep-images",
    help="Flag to keep downloaded manga images",
    type=bool,
    default=False,
)
args = parser.parse_args()


if not args.url:
    parser.print_help()
    exit(0)


md = MangaDownloader(
    url=args.m,
    keep_images=args.keep_images,
)
