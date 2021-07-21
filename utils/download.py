import os, sys
import time
import subprocess
import urllib.request as Request
import zipfile
from pathlib import Path
from prettyprinter import pprint

import logging
logger = logging.getLogger(__name__)

class Downloader():
    def __init__(self):
        pass

    def download(self, url, save_folder):
        print(url)

        save_name = os.path.split(url)[-1]

        self.url = url
        self.dst = Path(save_folder) / save_name
        self.save_folder = Path(os.path.split(self.dst)[0])
        self.unzip_folder = self.save_folder / "unzipped"

        logging.basicConfig(
            format='%(asctime)s %(levelname)s %(message)s',
            level=logging.INFO,
            stream=sys.stdout)   

        if os.path.isfile(self.dst):
            os.system("rm {}".format(self.dst))
            logging.info("Existed file deleted: {}".format(self.dst))
        else:
            logging.info("File doesn't exist.")
        # replace with url you need

        # if dir 'dir_name/' doesn't exist
        if not os.path.exists(self.save_folder):
            logging.info("Make direction: {}".format(self.save_folder))
            os.mkdir(self.save_folder)

        def down(_save_path, _url):
            try:
                Request.urlretrieve(_url, _save_path)
                return True
            except:
                print('\nError when retrieving the URL:\n{}'.format(_url))
                return False

        # logging.info("Downloading file.")
        down(self.dst, self.url)
        print("------- Download Finished! ---------\n")


    def un_zip(self, src):
        save_folder = Path(os.path.split(src)[0])
    
        unzip_folder = save_folder / "unzipped" / os.path.split(src)[-1][:-4]

        """ unzip zip file """
        zip_file = zipfile.ZipFile(src)
        if os.path.isdir(unzip_folder):
            pass
        else:
            os.mkdir(unzip_folder)
        for names in zip_file.namelist():
            zip_file.extract(names, unzip_folder)
        zip_file.close()