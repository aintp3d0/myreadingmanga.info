import anyio


SITE_HOST: str = "https://myreadingmanga.info"
STATIC_DIRECTORY: anyio.Path = anyio.Path("static")


# TODO
# check that `/manga` is not a `tag`
# - "https://myreadingmanga.info/tag/"
