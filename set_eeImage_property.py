
import os, subprocess
import json
from pathlib import Path
from easydict import EasyDict as edict
from datetime import datetime, timedelta
from prettyprinter import pprint

import ee
ee.Initialize()

def load_json(url) -> edict:
    with open(url, 'r') as fp:
        data = edict(json.load(fp))
    return data


# https://developers.google.com/earth-engine/guides/command_line
# collection_folder = "projects/ee-globalchange-gee4geo/assets/Sentinel1/"
collection_folder = "users/omegazhangpzh/Sentinel1/"

fileList = [
    "S1A_IW_GRDH_1SDV_20210720T141310_20210720T141327_038862_0495F7_B2E8",
    # "S1A_IW_GRDH_1SDV_20210720T141151_20210720T141220_038862_0495F7_D53A",
]


eeUser = "omegazhangpzh"
gs_dir = "gs://sar4wildfire/Sentinel1"
folder = "S1_GRD_2021-07-20T193552"

import glob
json_folder = Path("D:/Sentinel_Hub/outputs/BC_ROIS")
json_url = sorted(glob.glob(str(json_folder / f"{folder}.json")))[-1]
print("\njson: " + os.path.split(json_url)[-1])

query_info = load_json(json_url)

from update_sentinel_for_gee import set_image_property

fileListCopy = fileList.copy()

while(len(fileListCopy) > 0):
    # time.sleep(10) # wait?
    imgCol_name = os.path.split(gs_dir)[-1]
    response = subprocess.getstatusoutput(f"earthengine ls users/{eeUser}/{imgCol_name}")
    asset_list = response[1].replace("projects/earthengine-legacy/assets/", "").split("\n")

    for filename in fileList:
        asset_id = "users/omegazhangpzh/Sentinel1/" + filename

        if asset_id in asset_list:
            set_image_property(asset_id, query_info)
            fileListCopy.remove(filename)
        else:
            print(f"{asset_id} [Not Ready in GEE!]")



