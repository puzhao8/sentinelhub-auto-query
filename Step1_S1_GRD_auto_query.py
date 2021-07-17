
# Reference
# https://sentinelsat.readthedocs.io/en/master/_modules/sentinelsat/sentinel.html?highlight=offline#

from inspect import indentsize
import time, os
import json
import datetime
from datetime import datetime, timedelta
from pathlib import Path
from easydict import EasyDict as edict
from prettyprinter import pprint

from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt

import ee
import sentinelsat
ee.Initialize()


def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False

# api = SentinelAPI('puzhao', 'kth10044ESA!', 'https://scihub.copernicus.eu/dhus')
api = SentinelAPI('ahui0911', '19940911', 'https://scihub.copernicus.eu/dhus')

now = datetime.now().strftime("%Y-%m-%dT%H%M%S")
today = datetime.today().strftime("%Y-%m-%d")
start_date = (datetime.today() + timedelta(-2)).strftime("%Y-%m-%d")
end_date = (datetime.today() + timedelta(2)).strftime("%Y-%m-%d")
print("now: ", now)

cfg = edict({
    "roi_url": "inputs/BC_ROIs.geojson",
    "query_date": today,
    "start_date": start_date,
    "end_date": end_date,

    "platformname": "Sentinel-1",
    "producttype": 'GRD',
    # 'relativeorbitnumber': 84,
    # "orbitdirection": "ASCENDING",

    "download_one": True, # download one by one
    "download_all": True, # download all once

})

cfg.download_all = False if cfg.download_one  else True

# cmd
def sentinelsat_cmd_download(uuid, filename, path):
    user = "ahui0911"
    password = "19940911"
    geojson_url = path / f"{filename}.geojson"
    os.system(f"sentinelsat -u {user} -p {password}  --uuid {uuid} -d --path {path} \
        --footprints {geojson_url}")


workpath = Path(os.getcwd())
footprint = geojson_to_wkt(read_geojson(str(workpath / cfg.roi_url)))

# BC = placename_to_wkt("British Columbia")
# print(BC)

### DSC rorb = 22
products = api.query(
                        footprint, 
                        date=(cfg.start_date.replace("-",""), cfg.end_date.replace("-","")), 
                        platformname=cfg.platformname,
                        producttype=cfg.producttype,
                        #  relativeorbitnumber=84, 
                        # orbitdirection="ASCENDING", 
                        order_by='+beginposition',
                        # sensoroperationalmode='IW',
                        # filename='S1A*'
                    )

# print(products['0c05435b-0cd3-45a0-93f4-8c317eb1d558'])
print("\n\n===========> Sentinel Auto-Query <============")



products_df = api.to_dataframe(products)
# print(products_df.keys())
# print(products_df.index)
# pprint(products_df[['sensoroperationalmode', 'orbitdirection', 'relativeorbitnumber']])


products_dict = products_df.transpose().to_dict()
example_dict = products_dict[products_df.index.tolist()[0]]
property_list = [key for key in example_dict.keys() if is_jsonable(example_dict[key])]
# pprint(products_dict.keys())


# select property for saving to json
orbit_dict = {'ASCENDING': 'ASC', 'DESCENDING': 'DSC'}
products_to_save = edict()
S1 = ee.ImageCollection(f"COPERNICUS/S1_GRD")
for product_id in products_dict.keys():
    
    title = products_dict[product_id]['title']
    flag = (S1.filter(ee.Filter.eq("system:index", title)).size().getInfo()) > 0 
    print(title, flag)
    if not flag: # if this product is not available in GEE
        # print(title)
        # print(title, flag.getInfo())
        products_to_save[title] = {key: products_dict[product_id][key] for key in property_list}
        # products_to_save[title]['product_id'] = product_id

        orbit_direction = products_dict[product_id]['orbitdirection']
        orbit_num = products_dict[product_id]['relativeorbitnumber']

        products_to_save[title]['orbit_key'] = orbit_dict[orbit_direction] + "_" + str(orbit_num)

TO_SAVE = edict()
TO_SAVE["products"] = products_to_save

TO_SAVE["results"] = edict()
TO_SAVE["results"]['total_number'] = len(products_to_save.keys())
TO_SAVE["results"]['products_list'] = sorted(list(products_to_save.keys()))
TO_SAVE["results"]['orbKey_list'] = list(set([products_to_save[product]['orbit_key'] for product in list(products_to_save.keys())]))

TO_SAVE["cfg"] = cfg


roi_name = os.path.split(cfg.roi_url)[-1].split(".")[0]
savePath = workpath / "outputs" / roi_name
if not os.path.exists(str(savePath)):
    os.makedirs(savePath)

# save to json
json_url = savePath / f"S1_{cfg.producttype}_{now}.json"
print("\njson_url: " + str(json_url))

with open(str(json_url), 'w') as fp:
    json.dump(edict(TO_SAVE), fp, ensure_ascii=False, indent=4)


""" save as geojson """
import geojson
with open(savePath / f"S1_{cfg.producttype}_{now}.geojson", 'w') as fp:
   geojson.dump(api.to_geojson(products), fp, indent=4)


print()
print(footprint)
print("\nTotal Number of Searched Products:" + str(len(TO_SAVE["results"]['products_list'])))


""" If a product doesn't exist, then download one by one. """ 
if cfg.download_one:
    # dataPath = Path("G:/PyProjects/sentinelhub-auto-query/data/S1_GRD")
    dataPath = workpath / "data" / "S1_GRD"
    # for key in products.keys():
    for filename in TO_SAVE["results"]['products_list']:
        # filename = products[key]['title']
        uuid = TO_SAVE["products"][filename]['uuid']

        if os.path.exists(str(dataPath / f"{filename}.zip")):
            print(filename + " existed!")
        else:
            sentinelsat_cmd_download(uuid, filename, dataPath)
            # api.download(id=uuid, directory_path=dataPath, checksum=True)


""" download all once. """
if cfg.download_all:
    to_download_products = {}
    for filename in TO_SAVE["results"]['products_list']:
        uuid = TO_SAVE["products"][filename]['uuid']
        to_download_products[uuid] = TO_SAVE["products"][filename]

    # print(to_download_products)

    # api.download_all(to_download_products, directory_path=savePath, 
    #             max_attempts=10, checksum=True, n_concurrent_dl=1, let_retry_delay=600)

    api.download_all(products_df.index, directory_path=savePath, 
                max_attempts=10, checksum=True, n_concurrent_dl=1, let_retry_delay=600)




    