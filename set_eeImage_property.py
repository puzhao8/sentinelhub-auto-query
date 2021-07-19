
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
    "S1A_IW_GRDH_1SDV_20210719T013812_20210719T013841_038840_04954C_43AA",
    "S1A_IW_GRDH_1SDV_20210719T013841_20210719T013906_038840_04954C_ED6C",
    "S1A_IW_GRDH_1SDV_20210719T013906_20210719T013931_038840_04954C_9B58",
    "S1A_IW_GRDH_1SDV_20210719T013931_20210719T013956_038840_04954C_27C5",
    "S1A_IW_GRDH_1SDV_20210719T013956_20210719T014021_038840_04954C_6EB5",
    "S1A_IW_GRDH_1SDV_20210719T014021_20210719T014043_038840_04954C_EF05"
]



eeUser = "omegazhangpzh"
gs_dir = "gs://sar4wildfire/Sentinel1"
folder = "S1_GRD"

import glob
json_folder = Path("G:/PyProjects/sentinelhub-auto-query/outputs/BC_ROIs")
json_url = sorted(glob.glob(str(json_folder / f"{folder}*.json")))[-1]
print("\njson: " + os.path.split(json_url)[-1])

query_info = load_json(json_url)

from main_product_wise_auto_upload import set_image_property

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



