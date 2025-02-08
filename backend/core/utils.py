from .const import SITE_HOST


def is_site_host(url: str):
    return bool(url.startswith(SITE_HOST))
