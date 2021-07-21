from http.client import responses
import json
from easydict import EasyDict as edict
from ntpath import join
import ee
import os, sys
import time
import subprocess
import urllib.request as Request
import zipfile
from pathlib import Path
from prettyprinter import pprint

ee.Initialize()

from utils.download import Downloader
from utils.check_asset_public import check_asset_permission


def download_and_upload(url, save_folder, bucket="sar4wildfire"):
    filename = os.path.split(url)[-1][:-4]

    downloader = Downloader()
    downloader.download(url, save_folder)
    # # downloader.un_zip(save_folder / f"{filename}.zip")

    asset_id = f"users/omegazhangpzh/NRT_AF/{filename}"
    
    upload_to_bucket = f"gsutil -m cp -r {save_folder}/{filename}.zip gs://{bucket}/active_fire/{filename}.zip"
    # remove_asset = f"earthengine rm {asset_id}"
    ee_upload_table = f"earthengine upload table --force --asset_id={asset_id} gs://{bucket}/active_fire/{filename}.zip"

    os.system(upload_to_bucket)
    # if asset_id in asset_list:
    #     os.system(remove_asset)
    
    # os.system(ee_upload_table)

    ee_upload_response = subprocess.getstatusoutput(ee_upload_table)[1]
    task_id = ee_upload_response.split("ID: ")[-1]
    
    print(f"\n{asset_id}")
    pprint(f"task id: {task_id}")

    return filename, task_id

def upadte_active_fire(period_list = ['24h', '7d']):
    nasa_website = "https://firms.modaps.eosdis.nasa.gov"
    # save_folder = Path("D://firms-active-fire/outputs")
    save_folder = Path(os.getcwd()) / "outputs"

    if not os.path.exists(save_folder): os.makedirs(save_folder)
    
    firms = [
        "/data/active_fire/modis-c6.1/shapes/zips/MODIS_C6_1_Global_24h.zip",
        "/data/active_fire/suomi-npp-viirs-c2/shapes/zips/SUOMI_VIIRS_C2_Global_24h.zip",
        "/data/active_fire/noaa-20-viirs-c2/shapes/zips/J1_VIIRS_C2_Global_24h.zip"
    ]

    NRT_AF = subprocess.getstatusoutput("earthengine ls users/omegazhangpzh/NRT_AF/")
    # pprint(asset_list)

    """ Download and Upload into GEE """
    print("=============> Download and Upload into GEE <===============")
    task_dict = {}
    for period_key in period_list: # '48h', '7d
        for i in range(len(firms)):
            url = nasa_website + firms[i]
            url = url.replace("24h", period_key)

            filename, task_id = download_and_upload(url, save_folder, bucket="sar4wildfire")
            task_dict.update({filename: {'id': task_id}})

            
    """ check upload status """
    print("=============> check upload status <===============")
    upload_finish_flag = False
    while(not upload_finish_flag):
        print("-------------------------------------------------------")
        time.sleep(10) # delay 30s
        
        upload_finish_flag = True
        for filename in task_dict.keys():

            asset_id = f"users/omegazhangpzh/NRT_AF/{filename}"
            task_id = task_dict[filename]['id']

            check_upload_status = f"earthengine task info {task_id}"
            response = subprocess.getstatusoutput(check_upload_status)[1]
            state = response.split("\n")[1].split(": ")[-1]
            # state = edict(json.loads(response))['state']

            task_dict[filename].update({'state': state})

            if state == "COMPLETED":
                os.system(f"earthengine acl set public {asset_id}")

            # elif state == "FAILED":
            #     url_postfix = [i for i in firms if filename in firms[i]][0]
            #     url = nasa_website + url_postfix

            #     filename, task_id = download_and_upload(url, save_folder)
            #     task_dict.update({filename: {'id': task_id}})

            else:
                upload_finish_flag = False

            # check_asset_permission(asset_id)
            print(f"{asset_id}: {state}")

        print()
        # pprint(task_dict)

    
    """ set asset public """
    print("=============> set asset public <===============")
    asset_list = NRT_AF[1].replace("projects/earthengine-legacy/assets/", "").split("\n")
    for asset_id in asset_list:
        public_flag = check_asset_permission(asset_id)
        if not public_flag: 
            os.system(f"earthengine acl set public {asset_id}")


def set_AF_date(feat): 
    return feat.set("af_date", ee.Date(feat.get("ACQ_DATE")).format().slice(0,19))


if __name__ == "__main__":

    from datetime import datetime

    # while(True):
    now = datetime.now()
    current_time =  datetime.now().strftime("%H:%M:%S")

    # if current_time == "07:00:00":
        
        # time_split = current_time.split(":")
        # print(time_split)
    
        # if (int(time_split[0]) % 3 == 0) and (int(time_split[1])==0) and (int(time_split[2])==0):
            
    upadte_active_fire(period_list=['24h', '7d', '48h']) #  

    AF_SUOMI_VIIRS = ee.FeatureCollection("users/omegazhangpzh/NRT_AF/SUOMI_VIIRS_C2_Global_24h")
    AF = AF_SUOMI_VIIRS.map(set_AF_date)

    print(f"\n------------------> update time: {current_time} <-------------------")
    print(AF.aggregate_array("af_date").distinct().sort().getInfo()[-1])

    # time.sleep(60*60) # sleep 1h




    

        
                
