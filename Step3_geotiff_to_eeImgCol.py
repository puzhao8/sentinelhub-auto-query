

from itertools import product
import os, subprocess, time, json
from datetime import datetime
from easydict import EasyDict as edict
from pathlib import Path
from prettyprinter import pprint

import ee
ee.Initialize()

def load_json(url) -> edict:
    with open(url, 'r') as fp:
        data = edict(json.load(fp))
    return data


def set_image_property(asset_id, json_url):
    # json_folder = Path("G:/PyProjects/sentinelhub-auto-query/outputs/BC_ROI_2")
    # latest_json = sorted(os.listdir(json_folder))[-1]
    # json_url = json_folder / latest_json

    product_id = os.path.split(asset_id)[-1]

    query_info = load_json(json_url)
    product_info = query_info['products'][product_id]

    time_start = datetime.strptime(product_id.split("_")[4], "%Y%m%dT%H%M%S").strftime("%Y-%m-%dT%H:%M:%S")
    time_end = datetime.strptime(product_id.split("_")[5], "%Y%m%dT%H%M%S").strftime("%Y-%m-%dT%H:%M:%S")
    # footprint = product_info['footprint']

    print()
    pprint(product_id)
    print("-----------------------------------------------------------------")
    print(time_start)
    # print(footprint)

    os.system(f"earthengine asset set --time_start {time_start} {asset_id}")
    os.system(f"earthengine asset set --time_end {time_end} {asset_id}")

    property_dict = {
        'relativeorbitnumber': 'relativeOrbitNumber_start',
        'orbitdirection': 'orbitProperties_pass',
    }

    for property in product_info.keys():
        value = product_info[property]

        if property in property_dict.keys(): property = property_dict[property]

        print(property, value)    
        os.system(f"earthengine asset set -p {property}={value} {asset_id}")

    os.system(f"earthengine asset set -p {'gee'}={'false'} {asset_id}")
    # os.system(f"earthengine asset set -p {'transmitterReceiverPolarisation'}={'[VH, VV]'} {asset_id}")


if __name__ == "__main__":
    dataPath = Path("G:/PyProjects/sentinelhub-auto-query/outputs/S1_GRD_0716")
    cogPath = dataPath / "COG"
    
    gs_dir = "gs://wildfire-nrt/Sentinel1/"

    eeImgCol_name = os.path.split(gs_dir)[-1]
    eeImgCol = f"users/omegazhangpzh/{eeImgCol_name}"

    if not os.path.exists(cogPath): os.makedirs(cogPath)

    # print(dataPath)
    # print(os.listdir(dataPath))

    S1 = ee.ImageCollection("COPERNICUS/S1_GRD")
    S2 = ee.ImageCollection("COPERNICUS/S2")

    fileList = [filename for filename in os.listdir(dataPath) 
                    if (".tif" in filename) # this product doesn't exist in GEE
                        and S1.filter(ee.Filter.eq("system:index", filename[:-4])).size().getInfo() == 0 # if not exist in S1 of GEE
                        and S2.filter(ee.Filter.eq("PRODUCT_ID", filename[:-4])).size().getInfo() == 0 # if not exist in S2 of GEE
                ]

    pprint(fileList)


    # fileList = [
    #     # "S1B_IW_GRDH_1SDV_20210716T020155_20210716T020220_027813_0351A3_E556",
    #     "S1B_IW_GRDH_1SDV_20210716T020220_20210716T020245_027813_0351A3_0B43.tif",
    #     "S1B_IW_GRDH_1SDV_20210716T020245_20210716T020310_027813_0351A3_29DF.tif"
    # ]

    upload_flag = True

    """ To COG GeoTiff """
    if upload_flag:

        for filename in fileList:
            print()
            print(filename)
            print("---------------------------------------------------------")

            src_url = dataPath / filename
            dst_url = cogPath / filename
            os.system(f"gdal_translate {src_url} {dst_url} -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW")

        """ Upload COG into GCS """
        os.system(f"gsutil -m cp -r {cogPath}/* {gs_dir}")
        # os.rmdir(cogPath) # delete cog folder after uploading.

        """ Upload to earth engine asset """
        task_dict = {}
        for filename in os.listdir(cogPath):
            print(f"\n{filename[:-4]}")
            print("--------------------------------------------------------------------")

            asset_id = f"{eeImgCol}/{filename[:-4]}"
            ee_upload_image = f"earthengine upload image --asset_id={asset_id} {gs_dir}/{filename}"

            ee_upload_response = subprocess.getstatusoutput(ee_upload_image)[1]
            task_id = ee_upload_response.split("ID: ")[-1]
            task_dict.update({filename: {'task_id': task_id, 'asset_id': asset_id}})

            print(f"{asset_id}")
            pprint(f"task id: {task_id}\n")


        """ get property json """
        json_folder = Path("G:/PyProjects/sentinelhub-auto-query/outputs/BC_ROIs")
        latest_json = sorted(os.listdir(json_folder))[-1]
        json_url = json_folder / latest_json

        """ check uplpad status """
        print("=============> check uplpad status <===============")
        upload_finish_flag = False
        while(not upload_finish_flag):
            print("-------------------------------------------------------")
            time.sleep(60) # delay 30s
            
            upload_finish_flag = True
            for filename in task_dict.keys():

                asset_id = task_dict[filename]['asset_id'] #f"users/omegazhangpzh/Sentinel1/{filename}"
                task_id = task_dict[filename]['task_id']

                check_upload_status = f"earthengine task info {task_id}"
                response = subprocess.getstatusoutput(check_upload_status)[1]
                state = response.split("\n")[1].split(": ")[-1]
                # state = edict(json.loads(response))['state']

                task_dict[filename].update({'state': state})

                if state == "COMPLETED":
                    os.system(f"earthengine acl set public {asset_id}")

                    # """ Set Properties """
                    set_image_property(asset_id, json_url)
                else:
                    upload_finish_flag = False

                # check_asset_permission(asset_id)
                print(f"\n{asset_id}: {state}")

            print()
            # pprint(task_dict)




