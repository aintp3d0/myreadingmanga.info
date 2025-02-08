from litestar import Litestar, Controller, get, post, exceptions, status_codes

from core import const, utils


class Index(Controller):
    path = "/"

    @get()
    async def handler(self) -> None: ...


class Manga(Controller):
    path = "/manga"

    @get()
    async def get(
        self,
    ) -> None: ...

    @post()
    async def post(
        self,
        url: str,
        remove_images: bool,
    ) -> None:
        """Adding manga to process

        Parameters
        ----------
        url : str
            URL to the manga page
        remove_images : bool
            Flag to remove images after downloading
        """
        if not utils.is_site_host(url=url):
            raise exceptions.HTTPException(
                url,
                detail=f"URL must start with: {const.SITE_HOST}",
                status_code=status_codes.HTTP_417_EXPECTATION_FAILED,
            )
        print(remove_images)


app = Litestar(route_handlers=[Index, Manga])
