#!/usr/bin/env python3
# coding=utf-8

# __author__ = 'Nodaa Gaji'

import argparse
from os import getcwd, mkdir, chdir
from sys import path
from time import sleep
from wget import download
from random import randint
from shutil import copy, rmtree, move
from os.path import exists, dirname
from img2pdf import convert
from bs4 import BeautifulSoup as bs
from requests import get

"""
--m tag | wanna add chapter look up
"""


def get_soup(url):
    return bs(get(url).text, 'lxml')


class Yaoi:

    def __init__(self):
        self._link = None
        self._save_photos = None
        self._register_imgs = []
        self._list_of_pages = set()
        self._list_of_chapters = set()
        self._sort_manga_pages = []
        self._cur_dir = getcwd()
        self._manga = self._cur_dir + "/manga"
        self._save = self._cur_dir + "/saved"

    def _check_exists(self):
        if not exists(self._manga):
            mkdir(self._manga)
        if not exists(self._save):
            mkdir(self._save)

    def _get_tag_links(self, pg, sp):
        if pg:
            list_of_manga = sp.find_all('a', 'entry-title-link')
            for mg in list_of_manga:
                self._list_of_pages.add(mg.get('href'))
        else:
            soup = get_soup(sp)
            list_of_manga = soup.find_all('a', 'entry-title-link')
            for mg in list_of_manga:
                self._list_of_pages.add(mg.get('href'))

    def _get_tag(self):
        if self._link.startswith('https://myreadingmanga.info/tag/'):
            soup = get_soup(self._link)
            list_of_pages = soup.find_all('a')
            pages = set()
            for page in list_of_pages:
                try:
                    pk = page.get('href')
                    if '/page/' in pk:
                        pages.add(pk)
                except Exception as e:
                    print(e)
            self._get_tag_links(True, soup)
            if pages:
                for page in pages:
                    self._get_tag_links(False, page)
        else:
            self._list_of_pages.add(self._link)

    def _get_link(self, ch, ch_name):
        self._check_exists()
        for full_tag in self._list_of_pages:
            soup = get_soup(full_tag)
            images = soup.find_all('img')
            for image in images:
                pgs = image.get('src')
                if "bp.blogspot.com" in pgs and not pgs.endswith(".gif"):
                    self._sort_manga_pages.append(pgs)
            # search chapters
            if ch:
                chapters = soup.find('div', 'entry-pagination pagination')
                if chapters:
                    for chapter in chapters.find_all('a'):
                        try:
                            self._list_of_chapters.add(chapter.get('href'))
                        except Exception as e:
                            print(e)
            else:
                self._list_of_chapters = False
            self._get_manga(full_tag, ch_name)
        if self._list_of_chapters:
            self._list_of_pages = self._list_of_chapters
            self._get_link(False, True)

    def _get_manga(self, ft, ch):
        chdir(self._save)
        if ch:
            name = f"{ft.split('/')[-3]}_{ft.split('/')[-2]}"
        else:
            name = ft.split('/')[-2]
        if not exists(name):
            mkdir(name)
            chdir(name)
        else:
            new_ = randint(0, 126)
            name += str(new_)
            mkdir(name)
            chdir(name)
        for i in self._sort_manga_pages:
            if i.startswith('//'):
                i = 'http:' + i
            id_ = download(i)
            self._register_imgs.append(id_)
        self._convert_to_pdf(name)
        self._sort_manga_pages.clear()

    def _convert_to_pdf(self, name):
        r"""
                                            copy pdf to folder [ manga ] don't remove manga images
        [--s | None] -> convert_to_pdf __ /
                                          \
                                            move pdf to folder [ manga ] and remove current folder
        """
        pdf_ = name + ".pdf"
        with open(pdf_, 'wb') as file:
            ppt = [exists(pth) for pth in self._register_imgs]
            if all(ppt):
                # file.write(convert(self._register_imgs))
                file.write(convert([i for i in self._register_imgs]))
                if self._save_photos:
                    copy(pdf_, self._manga + '/' + pdf_)
                else:
                    move(pdf_, self._manga + '/' + pdf_)
                    rmtree(self._save + '/' + name)
            else:
                print('all: ', ppt)
                rmtree(self._save + '/' + name)
        self._register_imgs.clear()
        # bugg


    def _get_user_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--m", help="Download this manga", type=str)
        parser.add_argument("--s", help="Don't remove downloaded manga photos", type=str)
        args = parser.parse_args()

        self._link = args.m
        self._save_photos = args.s
        if args.m == args.s:
            print("""
    start_.py -h

                                        EXM:
                    [if you need to save downloaded manga photos]
    --m https://myreadingmanga.info/seki-sabato-tsukuru-matsuri-no-mae-kr/ --s true

                            [if you need Only pdf manga]
    --m https://myreadingmanga.info/seki-sabato-tsukuru-matsuri-no-mae-kr/
            """)
            exit(0)


if __name__ == "__main__":
    yo = Yaoi()
    yo._get_user_args()
    yo._get_tag()
    yo._get_link(True, False)
