
# Reference
# https://sentinelsat.readthedocs.io/en/master/_modules/sentinelsat/sentinel.html?highlight=offline#

from inspect import indentsize
import time, os
import json
from datetime import datetime, timedelta
from pathlib import Path
from easydict import EasyDict as edict
from prettyprinter import pprint

from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt, placename_to_wkt

import ee
import sentinelsat
ee.Initialize()


def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False

# cmd
def sentinelsat_cmd_download(uuid, filename, path, user="puzhao", password="kth10044ESA!"):
    geojson_url = path / f"{filename}.geojson"

    print(f"\n{filename}")
    os.system(f"sentinelsat -u {user} -p {password}  --uuid {uuid} -d --path {path} \
        --footprints {geojson_url}")

def query_sentinel_data(cfg, save_json=True):
    workpath = Path(os.getcwd())


    # api = SentinelAPI('puzhao', 'kth10044ESA!', 'https://scihub.copernicus.eu/dhus')
    # user, password = "ahui0911", "19940911"

    api = SentinelAPI(cfg.user, cfg.password, 'https://scihub.copernicus.eu/dhus')

    now = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    today = datetime.today().strftime("%Y-%m-%d")
    if cfg.start_date is None: cfg.start_date = (datetime.today() + timedelta(-1)).strftime("%Y-%m-%d")
    if cfg.end_date is None: cfg.end_date = (datetime.today() + timedelta(1)).strftime("%Y-%m-%d")
    print("now: ", now)

    cfg.update({
        "roi_url": cfg.roi_url,
        'placename': "British Columbia",
        "query_by": "roi", # 'place' has problem

        "query_date": today,
        "start_date": cfg.start_date,
        "end_date": cfg.end_date,

        "platformname": cfg.platformname, # Sentinel-2
        "producttype": cfg.producttype, # S2MSI1C, S2MSI2A

        # 'relativeorbitnumber': 84,
        # "orbitdirection": "ASCENDING",

        "download_flag": cfg.download_flag,
        "download_one": True, # download one by one
        "download_all": True, # download all once
    })

    pprint(cfg)

    Sat_Abb_Dict = {
        'Sentinel-1': 'S1',
        'Sentinel-2': 'S2',
        'Sentinel-3': 'S3'
    }
    SAT = Sat_Abb_Dict[cfg.platformname]

    datafolder = Path(cfg.datafolder)
    savePath = datafolder / "data" / f"{SAT}_{cfg.producttype}"
    if not os.path.exists(savePath): os.makedirs(savePath)

    cfg.update({"sat_folder": str(savePath)})
    
    cfg.download_all = False if cfg.download_one  else True
    cfg.download_all = cfg.download_all and cfg.download_flag
    cfg.download_one = cfg.download_one and cfg.download_flag

            
    if cfg.query_by == "roi":
        footprint = geojson_to_wkt(read_geojson(str(workpath / cfg.roi_url)))
        roi_name = os.path.split(cfg.roi_url)[-1].split(".")[0]

    if cfg.query_by == "place":
        footprint = placename_to_wkt(cfg.placename)
        roi_name = cfg.placename.replace(" ","_")
    # print(BC)

    ### DSC rorb = 22      
    if cfg.platformname == "Sentinel-1":
        cfg.checkProperty = "system:index"
        cfg.check_eeImgCol = "COPERNICUS/S1_GRD"

        products = api.query(
                            footprint, 
                            date=(cfg.start_date.replace("-",""), cfg.end_date.replace("-","")), 
                            platformname=cfg.platformname,
                            producttype=cfg.producttype,
                            order_by='+beginposition',
                        )
    
    else: # S2, S3 ...
        cfg.checkProperty = "PRODUCT_ID"
        cfg.check_eeImgCol = "COPERNICUS/S2"  if 'S2MSI1C' == cfg.producttype else "COPERNICUS/S2_SR"

        products = api.query(
                            footprint, 
                            date=(cfg.start_date.replace("-",""), cfg.end_date.replace("-","")), 
                            platformname=cfg.platformname,
                            producttype=cfg.producttype,
                            order_by='+beginposition',
                            cloudcoverpercentage=(0,cfg.cloudcoverpercentage), # for S2 only
                        )
    
    # print(products['0c05435b-0cd3-45a0-93f4-8c317eb1d558'])
    print("\n\n===========> Sentinel Auto-Query <============")

    products_df = api.to_dataframe(products)
    # print(products_df.keys())
    # print(products_df.index)
    # pprint(products_df[['sensoroperationalmode', 'orbitdirection', 'relativeorbitnumber']])

    products_dict = products_df.transpose().to_dict()
    
    products_list = products_df.index.tolist()
    if len(products_list) > 0: 
        example_dict = products_dict[products_list[0]]
        property_list = [key for key in example_dict.keys() if is_jsonable(example_dict[key])]
    # pprint(products_dict.keys())


    # select property for saving to json
    orbit_dict = {'ASCENDING': 'ASC', 'DESCENDING': 'DSC'}
    products_QueryInfo = edict()
    checkImgCol = ee.ImageCollection(f"{cfg.check_eeImgCol}")

    if SAT == "S1": 
        sentinel_asset = ee.ImageCollection("users/omegazhangpzh/Sentinel1")
    if SAT == "S2": 
        sentinel_asset = ee.ImageCollection("users/omegazhangpzh/Sentinel2")

    for product_id in products_dict.keys():
        title = products_dict[product_id]['title']
        filtered_size = ee.Number(checkImgCol.filter(ee.Filter.eq(cfg.checkProperty, title)).size())\
                    .add(sentinel_asset.filter(ee.Filter.eq(cfg.checkProperty, title)).size()).getInfo()
        flag = filtered_size > 0 
        print(title, flag)

        # flag = False
        if not flag: # if this product is not available in GEE
            # print(title)
            # print(title, flag.getInfo())
            products_QueryInfo[title] = {key: products_dict[product_id][key] for key in property_list}
            # products_QueryInfo[title]['product_id'] = product_id

            orbit_direction = products_dict[product_id]['orbitdirection']
            orbit_num = products_dict[product_id]['relativeorbitnumber']

            products_QueryInfo[title]['orbit_key'] = orbit_dict[orbit_direction] + "_" + str(orbit_num)

    QueryInfo = edict()
    QueryInfo["products"] = products_QueryInfo

    QueryInfo["results"] = edict()
    QueryInfo["results"]['total_number'] = len(products_QueryInfo.keys())
    QueryInfo["results"]['products_list'] = sorted(list(products_QueryInfo.keys()))
    QueryInfo["results"]['orbKey_list'] = list(set([products_QueryInfo[product]['orbit_key'] for product in list(products_QueryInfo.keys())]))

    QueryInfo["cfg"] = cfg


    # roi_name = os.path.split(cfg.roi_url)[-1].split(".")[0]
    jsonPath = datafolder / "outputs" / roi_name
    if not os.path.exists(str(jsonPath)):
        os.makedirs(jsonPath)

    if save_json:
        """ save as json """
        json_url = jsonPath / f"{SAT}_{cfg.producttype}_{now}.json"
        print("\njson_url: " + str(json_url))

        with open(str(json_url), 'w') as fp:
            json.dump(edict(QueryInfo), fp, ensure_ascii=False, indent=4)


        """ save as geojson """
        import geojson
        with open(jsonPath / f"S1_{cfg.producttype}_{now}.geojson", 'w') as fp:
            geojson.dump(api.to_geojson(products), fp, indent=4)


    print()
    # print(footprint)
    print("now: ", now)
    print("Total Number of Searched Products:" + str(len(QueryInfo["results"]['products_list'])))
    pprint(QueryInfo["results"]['products_list'])

    return QueryInfo


def download_sentinel_data(QueryInfo):
    cfg = QueryInfo.cfg
    sat_folder = Path(cfg.sat_folder)
    pprint(cfg)
    
    """ If a product doesn't exist, then download one by one. """ 
    if cfg.download_one:
        # savePath = Path("G:/PyProjects/sentinelhub-auto-query/data/S1_GRD")
        # savePath = workpath / "data" / "S1_GRD"
        # if not os.path.exists(savePath): os.makedirs(savePath)
        # for key in products.keys():
        for filename in QueryInfo["results"]['products_list']:
            # filename = products[key]['title']
            uuid = QueryInfo["products"][filename]['uuid']

            if os.path.exists(str(sat_folder / f"{filename}.zip")):
                print(filename + " [existed!]")
            else:
                sentinelsat_cmd_download(uuid, filename, sat_folder, cfg.user, cfg.password)
                # api.download(id=uuid, directory_path=savePath, checksum=True)


    # """ download all once. """
    # if cfg.download_all:
    #     to_download_products = {}
    #     for filename in QueryInfo["results"]['products_list']:
    #         uuid = QueryInfo["products"][filename]['uuid']
    #         to_download_products[uuid] = QueryInfo["products"][filename]

    #     # print(to_download_products)

    #     # api.download_all(to_download_products, directory_path=jsonPath, 
    #     #             max_attempts=10, checksum=True, n_concurrent_dl=1, let_retry_delay=600)

    #     api.download_all(products_df.index, directory_path=jsonPath, 
    #                 max_attempts=10, checksum=True, n_concurrent_dl=1, let_retry_delay=600)


if __name__ == "__main__":

    # cfg = edict({
    #     "roi_url": "inputs/BC_ROIs.geojson",

    #     "platformname": "Sentinel-1", # Sentinel-2
    #     "producttype": 'GRD', # S2MSI1C, S2MSI2A

    #     "start_date": None,
    #     "end_date": None,

    #     "download_flag": False,
    #     "datafolder": "D:/Sentinel_Hub", # where to save data
    
    # })

    # from config.sentinel1 import cfg
    from config.sentinel2 import cfg
    cfg = edict(cfg)

    query_info = query_sentinel_data(cfg)
    download_sentinel_data(query_info)

    



        