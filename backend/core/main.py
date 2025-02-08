from os import mkdir, chdir
from random import randint
from shutil import copy, rmtree, move
from os.path import exists
from pathlib import Path

from img2pdf import convert

from const import STATIC_DIRECTORY
from utils import get_soup


class MyReadingManga:
    __slots__ = (
        "url",
        "download_all_chapters",
        "keep_downloaded_images",
        "sorted_manga_images",
    )
    manga_directory: Path = STATIC_DIRECTORY / "manga"
    image_directory: Path = STATIC_DIRECTORY / "saved"
    manga_directory.mkdir(exist_ok=True)
    image_directory.mkdir(exist_ok=True)
    error_messages: list[str] = []
    process_result: list[str] = []

    def __init__(
        self,
        url: str,
        download_all_chapters: bool,
        keep_downloaded_images: bool,
    ):
        self.url = url
        self.keep_downloaded_images = keep_downloaded_images
        self.sorted_manga_images = []
        self._register_imgs = []
        self._list_of_pages = set()
        self._list_of_chapters = set()

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

    async def process(self, process_chapters: bool = True) -> None:
        """Processing the given manga `url`

        Parameters
        ----------
        process_chapters : bool = True
            Process chapters for given manga `url`
        """
        soup = await get_soup(self.url)

        for image in soup.find_all("img"):
            image_source = image.get("src")
            if "bp.blogspot.com" not in image_source:
                continue
            if image_source.endswith(".gif"):
                continue
            self.sorted_manga_images.append(image_source)

        # search chapters
        if ch:
            chapters = soup.find("div", "entry-pagination pagination")
            if chapters:
                for chapter in chapters.find_all("a"):
                    try:
                        self._list_of_chapters.add(chapter.get("href"))
                    except Exception as e:
                        print(e)

        self._get_manga(full_tag, ch_name)

        # FEAT: TODO/FIXME
        # if self._list_of_chapters:
        #     self._list_of_pages = self._list_of_chapters
        #     self._get_link(False, True)

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
