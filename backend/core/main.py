import asyncio
import shutil
from collections import defaultdict
from urllib.parse import urlparse

import anyio
import httpx
import img2pdf

from const import STATIC_DIRECTORY
from utils import get_soup


class MyReadingManga:
    """Downloading manga images and converting it to PDF

    process_result:
        chapters:
            link:
            images:
            manga:
    """

    __slots__ = (
        "url",
        "download_all_chapters",
        "keep_downloaded_images",
        "list_of_chapters",
        # TODO: Remove / Refactor
        "_register_imgs",
        "_list_of_pages",
    )
    manga_directory: anyio.Path = STATIC_DIRECTORY / "manga"
    image_directory: anyio.Path = STATIC_DIRECTORY / "saved"
    error_messages: dict[str, list[str]] = defaultdict(list)
    process_result: dict[str, list[str]] = defaultdict(list)

    def __init__(
        self,
        url: str,
        download_all_chapters: bool,
        keep_downloaded_images: bool,
    ):
        self.url = url
        self.download_all_chapters = download_all_chapters
        self.keep_downloaded_images = keep_downloaded_images
        self._register_imgs = []
        self._list_of_pages = set()
        self.list_of_chapters: list[str] = []

    # TODO: Refactor
    def _get_tag_links(self, pg, sp):
        if pg:
            list_of_manga = sp.find_all("a", "entry-title-link")
            for mg in list_of_manga:
                self._list_of_pages.add(mg.get("href"))
        else:
            soup = get_soup(sp)
            list_of_manga = soup.find_all("a", "entry-title-link")
            for mg in list_of_manga:
                self._list_of_pages.add(mg.get("href"))

    # TODO: Refactor
    def get_tag(self):
        # FEAT: get tags
        if self._link.startswith("https://myreadingmanga.info/tag/"):
            soup = get_soup(self._link)
            list_of_pages = soup.find_all("a")
            pages = set()
            for page in list_of_pages:
                try:
                    pk = page.get("href")
                    if "/page/" in pk:
                        pages.add(pk)
                except Exception as e:
                    print(e)
            self._get_tag_links(True, soup)
            if pages:
                for page in pages:
                    self._get_tag_links(False, page)
        else:
            self._list_of_pages.add(self._link)

    async def search_manga_chapters(self) -> None:
        """Search for manga chapters

        Returns `False` if chapters were not found
        """
        soup = await get_soup(self.url)

        chapters_pagination = soup.find(
            "div",
            class_="entry-pagination pagination",
        )
        if chapters_pagination is None:
            self.error_messages[self.url].append(
                "No chapters pagination were found!",
            )
            return

        chapters = chapters_pagination.find_all("a")
        if not chapters:
            self.error_messages[self.url].append(
                "No chapters url were found!",
            )
            return

        for chapter in chapters:
            chapter_url = chapter.get("href")
            if chapter_url is None:
                continue
            self.list_of_chapters.append(chapter_url)

        if not self.list_of_chapters:
            self.error_messages[self.url].append(
                "No chapters url were found!",
            )
            return

    async def download_chapter_image(
        self,
        chapter_url: str,
        chapter_path: anyio.Path,
        image_src: str,
        url_to_path: dict[str, str],
    ) -> None:
        """Downloading chapter image

        Parameters
        ----------
        chapter_url : str
        chapter_path : anyio.Path
            Path to save chapter images
        image_src : str
            Chapter image url
        url_to_path : dict[str, str]
            Combine `chapter_url` with `chapter_image_path`
        """
        image_path = chapter_path / image_src.rsplit("/", maxsplit=1)[-1]

        async with httpx.AsyncClient() as client:
            response = await client.get(image_src)
            if response.status_code != 200:
                self.error_messages[chapter_url].append(f"[?] {image_src}")
                return

        await image_path.write_bytes(response.content)

        if not (await image_path.exists()):
            self.error_messages[chapter_url].append(
                f"Chapeter Image is not downloaded: {image_src}"
            )
            return

        url_to_path[image_src] = image_path.as_posix()

    def gen_chapter_name(self, chapter_url: str) -> str:
        """Returns the generates chapter name"""
        # NOTE: No path validation
        return "-chapter-".join(
            filter(
                bool,
                urlparse(
                    url=chapter_url,
                ).path.split("/"),
            )
        )

    async def process_chapter(self, chapter_url: str) -> None:
        """Processing the given manga `chapter_url`

        - Find all images, keep their order
        - AsyncIO task to download
        - Convert to pdf with their order
        """
        sorted_chapter_images: list[str] = []
        url_to_path: dict[str, str] = {}

        soup = await get_soup(self.url)

        for image in soup.find_all("img"):
            image_source = image.get("src")
            # TODO: find out what `get` will return
            # - ignore for None
            if "bp.blogspot.com" not in image_source:
                continue
            if image_source.endswith(".gif"):
                continue
            sorted_chapter_images.append(image_source)

        if not sorted_chapter_images:
            self.error_messages[chapter_url].append(
                "No images were found",
            )
            return

        chapter_name = urlparse(chapter_url).path
        if not chapter_name:
            chapter_name = chapter_name

        chapter_name = self.gen_chapter_name(chapter_url)
        chapter_manga_path = anyio.Path(self.manga_directory / chapter_name)
        chapter_image_path = anyio.Path(self.image_directory / chapter_name)
        await chapter_manga_path.mkdir(parents=True, exist_ok=True)
        await chapter_image_path.mkdir(parents=True, exist_ok=True)

        async with asyncio.TaskGroup() as group:
            for chapter_image in sorted_chapter_images:
                group.create_task(
                    self.download_chapter_image(
                        chapter_url=chapter_url,
                        chapter_path=chapter_image_path,
                        image_src=chapter_image,
                        url_to_path=url_to_path,
                    )
                )

        if not url_to_path:
            self.error_messages[chapter_url].append(
                "No images were saved",
            )
            return

        await self.convert_chapter_to_pdf(
            chapter_url=chapter_url,
            chapter_name=chapter_name,
            chapter_manga_path=chapter_manga_path,
            chapter_image_path=chapter_image_path,
            sorted_chapter_images=sorted_chapter_images,
            url_to_path=url_to_path,
        )

    async def process(self) -> None:
        """Processing the given manga `url`"""
        if self.download_all_chapters:
            await self.search_manga_chapters()

        if not self.list_of_chapters:
            self.list_of_chapters.append(self.url)

        async with asyncio.TaskGroup() as group:
            for chapter_url in self.list_of_chapters:
                group.create_task(
                    self.process_chapter(chapter_url),
                )

    async def convert_chapter_to_pdf(
        self,
        chapter_url: str,
        chapter_name: str,
        chapter_manga_path: anyio.Path,
        chapter_image_path: anyio.Path,
        sorted_chapter_images: list[str],
        url_to_path: dict[str, str],
    ) -> None:
        """PDF convertion and clean up

        Removes downloaded images if `--keep-images` flag not set (default)
        """
        manga_filepath = chapter_manga_path / f"{chapter_name}.pdf"
        downloaded_chapter_images: list[str] = []

        for image_src in sorted_chapter_images:
            if image_src not in url_to_path:
                continue
            downloaded_chapter_images.append(url_to_path[image_src])

        manga_file = img2pdf.convert(downloaded_chapter_images)
        if manga_file is None:
            self.error_messages[chapter_url].append(
                "Could not convert chapter images of: "
                f"{len(downloaded_chapter_images)}",
            )
            return

        await manga_filepath.write_bytes(manga_file)

        if not self.keep_downloaded_images:
            shutil.rmtree(chapter_image_path)
