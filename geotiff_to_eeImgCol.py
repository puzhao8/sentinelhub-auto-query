


import os
from pathlib import Path 

dataPath = Path("G:/PyProjects/sentinelhub-auto-query/outputs/S1")
savePath = dataPath / "COG"
gs_dir = "gs://wildfire-nrt/S1/"
if not os.path.exists(savePath): os.makedirs(savePath)

# print(dataPath)
# print(os.listdir(dataPath))

fileList = [filename for filename in os.listdir(dataPath) if ".tif" in filename]


# print(list(set(fileList).symmetric_difference(set(gee_list))))

# fileList_ = list(set(fileList).symmetric_difference(set(gee_list)))

# print(fileList_)

""" To COG GeoTiff """
if False:
    for filename in fileList:
        print(filename)

        src_url = dataPath / filename
        dst_url = savePath / filename
        os.system(f"gdal_translate {src_url} {dst_url} -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW")


""" Upload COG into GCS """
os.system(f"gsutil -m cp -r {savePath}/* {gs_dir}")

""" Upload to earth engine asset """
if True:
    for filename in fileList:
        print(f"{filename[:-4]}: {filename}")
        # print(f"earthengine upload image --asset_id=users/omegazhangpzh/ESA_AGB_100m_2010/{filename[:-4]} {gs_dir}/{filename}")
        # os.system(f"earthengine upload image --asset_id=users/omegazhangpzh/NRT_AF/Sentinel-3/S3_{filename[:-4]} {gs_dir}/{filename}")
        asset_id = f"projects/ee-globalchange-gee4geo/assets/Sentinel1/{filename[:-4]}"
        os.system(f"earthengine upload image --asset_id={asset_id} {gs_dir}/{filename}")



""" Set Properties """
# if upload finish then set property 
# os.system(f"earthengine asset set -p '(string)name=42' users/username/asset_id")

# https://developers.google.com/earth-engine/guides/command_line
# earthengine asset info users/username/asset_id
# earthengine asset set -p name=value users/username/asset_id

earthengine asset info projects/ee-globalchange-gee4geo/assets/Sentinel1/S1B_IW_GRDH_1SDV_20210714T141147_20210714T141212_027791_035101_0B6B
earthengine asset set -p name=value projects/ee-globalchange-gee4geo/assets/Sentinel1/S1B_IW_GRDH_1SDV_20210714T141147_20210714T141212_027791_035101_0B6B

earthengine asset set -p name=value projects/ee-globalchange-gee4geo/assets/Sentinel1/S1B_IW_GRDH_1SDV_20210714T141147_20210714T141212_027791_035101_0B6B

earthengine asset set -p '(string)orbitdirection=DESCENDING' projects/ee-globalchange-gee4geo/assets/Sentinel1/S1B_IW_GRDH_1SDV_20210714T141147_20210714T141212_027791_035101_0B6B
earthengine asset set -p '(string)relativeorbitnumber=115' projects/ee-globalchange-gee4geo/assets/Sentinel1/S1B_IW_GRDH_1SDV_20210714T141147_20210714T141212_027791_035101_0B6B
