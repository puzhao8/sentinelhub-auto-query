
import os
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
    # "S1B_IW_GRDH_1SDV_20210716T020155_20210716T020220_027813_0351A3_E556",
    "S1B_IW_GRDH_1SDV_20210716T020220_20210716T020245_027813_0351A3_0B43",
    "S1B_IW_GRDH_1SDV_20210716T020245_20210716T020310_027813_0351A3_29DF"
]

for product_id in fileList:
    # product_id = "S1B_IW_GRDH_1SDV_20210714T141147_20210714T141212_027791_035101_0B6B"

    json_folder = Path("G:/PyProjects/sentinelhub-auto-query/outputs/BC_ROI_2")
    latest_json = sorted(os.listdir(json_folder))[-1]
    json_url = json_folder / latest_json

    query_info = load_json(json_url)
    product_info = query_info['products'][product_id]

    time_start = datetime.strptime(product_id.split("_")[4], "%Y%m%dT%H%M%S").strftime("%Y-%m-%dT%H:%M:%S")
    time_end = datetime.strptime(product_id.split("_")[5], "%Y%m%dT%H%M%S").strftime("%Y-%m-%dT%H:%M:%S")
    footprint = product_info['footprint']

    print()
    pprint(product_id)
    print("-----------------------------------------------------------------")
    print(time_start)
    # print(footprint)

    os.system(f"earthengine asset set --time_start {time_start} {collection_folder + product_id}")
    os.system(f"earthengine asset set --time_end {time_end} {collection_folder + product_id}")

    property_dict = {
        'relativeorbitnumber': 'relativeOrbitNumber_start',
        'orbitdirection': 'orbitProperties_pass',
    }

    for property in product_info.keys():
        value = product_info[property]

        if property in property_dict.keys(): property = property_dict[property]

        # if "footprint" == property: 
        #     # property = "footprint"
        #     string_list = value.split("(((")[1][:-3].replace(" ", ",").replace(",,", ",").split(",")
        #     value = [eval(x) for x in string_list]
        #     # value = ee.Geometry.MultiPolygon([-118.227242, 50.409222, -117.754776, 51.904125, -121.424622, 52.301323, -121.779961, 50.804768, -118.227242, 50.409222])

        print(property, value)    
        os.system(f"earthengine asset set -p {property}={value} {collection_folder + product_id}")

    os.system(f"earthengine asset set -p {'gee'}={'false'} {collection_folder + product_id}")
    # os.system(f"earthengine asset set -p {'transmitterReceiverPolarisation'}={'[VH, VV]'} {collection_folder + product_id}")
