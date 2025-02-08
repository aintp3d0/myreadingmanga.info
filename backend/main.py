from litestar import Litestar, Controller, get, post, exceptions, status_codes

from core import const, utils
from core.main import MangaDownloader


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
        keep_images: bool,
    ) -> None:
        """Adding manga to process

        Parameters
        ----------
        url : str
            URL to the manga page
        keep_images : bool
            Flag to keep downloaded images
        """
        if not utils.is_site_host(url=url):
            raise exceptions.HTTPException(
                url,
                detail=f"URL must start with: {const.SITE_HOST}",
                status_code=status_codes.HTTP_417_EXPECTATION_FAILED,
            )

        md = MangaDownloader(
            url=url,
            keep_images=keep_images,
        )
        # wait till the end
        is_processed = await md.process()
        if not is_processed:
            # TODO: serialize error messages
            return md.error_messages()

        # TODO: serialize result data
        return md.process_result()


app = Litestar(route_handlers=[Index, Manga])
