#!/usr/bin/env python3
# coding=utf-8

# __author__ = 'ames0k0'

from os import getcwd, mkdir, chdir
from sys import argv
from time import sleep
from wget import download
from random import randint
from shutil import copy, rmtree, move
from os.path import exists, dirname
from img2pdf import convert
from bs4 import BeautifulSoup as bs
from requests import get
from pathlib import Path


def get_file_soup(filename):
    with open(filename, 'r') as ftr:
        return bs(ftr.read(), 'lxml')


class Yaoi:

    def __init__(self, file):
        self.file = file
        self._register_imgs = []
        self._cur_dir = getcwd()
        self._manga = self._cur_dir + "/manga"
        # TODO
        self._save = self._cur_dir + "/saved"

    def _check_exists(self):
        if not exists(self._manga):
            mkdir(self._manga)
        if not exists(self._save):
            mkdir(self._save)

    def collect_images(self):
        self._check_exists()

        soup = get_file_soup(self.file)
        images = soup.find('div', 'entry-content').find_all('img')
        for image in images:
            pgs = image.get('src')
            if pgs.startswith('https'):
                continue
            if not exists(pgs):
                print('[Skip]', pgs)
                continue
            print('>', pgs)
            self._register_imgs.append(pgs)

    def convert_to_pdf(self):
        self.collect_images()

        pdf_ = self.file.stem + ".pdf"
        with open(pdf_, 'wb') as file:
            file.write(convert(self._register_imgs))

        # TODO: -s
        move(pdf_, self._manga + '/' + pdf_)


if __name__ == "__main__":
    if len(argv) == 1:
        print('Usage: python3 offline.py <downloaded_page.html> [optional -s]')
        exit()

    file = Path(argv[1])

    if not file.is_file():
        print('Argument is not a file')
        exit()

    if not file.exists():
        print('File is not exists!')
        exit()

    yo = Yaoi(file)
    yo.convert_to_pdf()
