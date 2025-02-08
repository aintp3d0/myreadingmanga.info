from litestar import Litestar, Controller, get, post, exceptions, status_codes

from core import const, utils
from core.main import MyReadingManga


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
        download_all_chapters: bool,
        keep_downloaded_images: bool,
    ) -> None:
        """Adding manga to process

        Parameters
        ----------
        url : str
            URL to the manga page
        download_all_chapters : bool
            Flag to download all chapters for the given `url`
        keep_downloaded_images : bool
            Flag to keep downloaded images
        """
        if not utils.is_site_host(url=url):
            raise exceptions.HTTPException(
                url,
                detail=f"URL must start with: {const.SITE_HOST}",
                status_code=status_codes.HTTP_417_EXPECTATION_FAILED,
            )

        mrm = MyReadingManga(
            url=url,
            download_all_chapters=download_all_chapters,
            keep_downloaded_images=keep_downloaded_images,
        )
        # wait till the end
        is_processed = await mrm.process()
        if not is_processed:
            # TODO: serialize error messages
            print(mrm.error_messages)

        # TODO: serialize result data
        print(mrm.process_result)


app = Litestar(route_handlers=[Index, Manga])
