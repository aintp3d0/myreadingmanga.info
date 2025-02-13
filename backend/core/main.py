import asyncio
from os import mkdir, chdir
from random import randint
from shutil import copy, rmtree, move
from os.path import exists
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse

import httpx
from img2pdf import convert

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
    )
    manga_directory: Path = STATIC_DIRECTORY / "manga"
    image_directory: Path = STATIC_DIRECTORY / "saved"
    manga_directory.mkdir(exist_ok=True)
    image_directory.mkdir(exist_ok=True)
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
        image_src: str,
        url_to_path: dict[str, str],
    ) -> None:
        """Downloading chapter image"""
        async with httpx.AsyncClient() as client:
            response = await client.get(image_src)
            if response.status_code != 200:
                self.error_messages[chapter_url].append(f"[?] {image_src}")
                return

            response.content

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

        chapter_path = anyio.Path()

        async with asyncio.TaskGroup() as group:
            for chapter_image in sorted_chapter_images:
                group.create_task(
                    self.download_chapter_image(
                        chapter_url=chapter_url,
                        image_src=chapter_image,
                        url_to_path=url_to_path,
                    )
                )

        self._get_manga(full_tag, ch_name)

    async def process(self) -> None:
        """Processing the given manga `url`"""
        if self.download_all_chapters:
            await self.search_manga_chapters()
            if not self.list_of_chapters:
                self.list_of_chapters.append(self.url)
        else:
            self.list_of_chapters.append(self.url)

        async with asyncio.TaskGroup() as group:
            for chapter_url in self.list_of_chapters:
                group.create_task(
                    self.process_chapter(chapter_url),
                )

    def _get_manga(self, ft, ch):
        chdir(self._save)
        if ch:
            name = f"{ft.split('/')[-3]}_{ft.split('/')[-2]}"
        else:
            name = ft.split("/")[-2]
        if not exists(name):
            mkdir(name)
            chdir(name)
        else:
            new_ = randint(0, 126)
            name += str(new_)
            mkdir(name)
            chdir(name)
        for i in self._sort_manga_pages:
            if i.startswith("//"):
                i = "http:" + i
            id_ = download(i)
            self._register_imgs.append(id_)
        self._convert_to_pdf(name)

    def _convert_to_pdf(self, name):
        """PDF convertion and clean up

        Removes downloaded images if `--s` flag not set (default)
        """
        pdf_ = name + ".pdf"
        with open(pdf_, "wb") as file:
            ppt = [exists(pth) for pth in self._register_imgs]
            if all(ppt):
                # file.write(convert(self._register_imgs))
                file.write(convert([i for i in self._register_imgs]))
                if self._save_photos:
                    copy(pdf_, self._manga + "/" + pdf_)
                else:
                    move(pdf_, self._manga + "/" + pdf_)
                    rmtree(self._save + "/" + name)
            else:
                print("all: ", ppt)
                rmtree(self._save + "/" + name)
