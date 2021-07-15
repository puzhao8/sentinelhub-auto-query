
# Reference
# https://sentinelsat.readthedocs.io/en/master/_modules/sentinelsat/sentinel.html?highlight=offline#
# https://force-eo.readthedocs.io/en/latest/howto/sentinel2-l1c.html

import time, os
import json
import datetime
from pathlib import Path
from easydict import EasyDict as edict
from prettyprinter import pprint

from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt

import ee
ee.Initialize()

def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False

api = SentinelAPI('ahui0911', '19940911', 'https://scihub.copernicus.eu/dhus')

cfg = edict({
    "roi_url": "inputs/BC_ROI_2.geojson",
    "start_date": "2021-07-14",
    "end_date": "2021-08-01",

    "platformname": "Sentinel-2",
    "producttype": 'S2MSI1C',
    # 'relativeorbitnumber': 84,
    # "orbitdirection": "ASCENDING",

})

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

print("\n\n===========> Sentinel-2 Auto-Query <============")

products_df = api.to_dataframe(products)
# print(products_df.keys())
# print(products_df.index)
# pprint(products_df[['sensoroperationalmode', 'orbitdirection', 'relativeorbitnumber']])


products_dict = products_df.transpose().to_dict()
example_dict = products_dict[products_df.index.tolist()[0]]
property_list = [key for key in example_dict.keys() if is_jsonable(example_dict[key])]
# pprint(products_dict.keys())


# select property for saving to json
products_to_save = edict()
S2 = ee.ImageCollection("COPERNICUS/S2")
for product_id in products_dict.keys():
    
    title = products_dict[product_id]['title']
    flag = ee.Algorithms.If(S2.filter(ee.Filter.eq("PRODUCT_ID", title)).size().gt(0), True, False)
    print(title, flag.getInfo())

    if not flag.getInfo(): # if this product is not available in GEE
        # print(title)
        # print(title, flag.getInfo())
        products_to_save[title] = {key: products_dict[product_id][key] for key in property_list}
        # products_to_save[title]['product_id'] = product_id


TO_SAVE = edict()
TO_SAVE["products"] = products_to_save

TO_SAVE["results"] = edict()
TO_SAVE["results"]['total_number'] = len(products_to_save.keys())
TO_SAVE["results"]['products_list'] = sorted(list(products_to_save.keys()))
# TO_SAVE["results"]['orbKey_list'] = list(set([products_to_save[product]['orbit_key'] for product in list(products_to_save.keys())]))

TO_SAVE["cfg"] = cfg


roi_name = os.path.split(cfg.roi_url)[-1].split(".")[0]
savePath = workpath / "outputs" / roi_name / cfg.platformname
if not os.path.exists(str(savePath)):
    os.makedirs(savePath)

# save to json
json_url = savePath / "S2.json"
with open(str(json_url), 'w') as fp:
    json.dump(edict(TO_SAVE), fp, ensure_ascii=False, indent=4)


print()
print(footprint)
print("\nTotal Number of Searched Products:" + str(len(products.keys())))



# api.download_all(products, savePath)


# print("\nData to download ...")
# print("------------------------------------------------------------------")
# for key in products.keys():
#     filename = products[key]['title']
#     print(filename)
# print("------------------------------------------------------------------")



### download all once.
# api.download_all(products, directory_path=savePath)


### If a product doesn't exist, then download one by one.
if False:
    for key in products.keys():
        filename = products[key]['title']

        if os.path.exists(str(savePath / "{filename}.zip")):
            print("existed: " + filename)

        else:
            print(filename)

            whileFlag = True
            while whileFlag:
                # print("Downloading: " + filename)

                try:
                    print("Tried in ==> {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    api.download(key, savePath)
                    whileFlag = False

                except:
                    whileFlag = True

                    time.sleep(10*60)
