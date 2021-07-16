

import os
from pathlib import Path
from prettyprinter import pprint

import ee
ee.Initialize()

dataPath = Path("G:/PyProjects/sentinelhub-auto-query/outputs/S1_GRD_0716")
savePath = dataPath / "COG"
gs_dir = "gs://wildfire-nrt/Sentinel1/"

if not os.path.exists(savePath): os.makedirs(savePath)

# print(dataPath)
# print(os.listdir(dataPath))

S1 = ee.ImageCollection("COPERNICUS/S1_GRD")
S2 = ee.ImageCollection("COPERNICUS/S2")

fileList = [filename for filename in os.listdir(dataPath) 
                if (".tif" in filename) # this product doesn't exist in GEE
                    # and S1.filter(ee.Filter.eq("system:index", filename[:-4])).size().getInfo() == 0 # if not exist in S1 of GEE
                    # and S2.filter(ee.Filter.eq("PRODUCT_ID", filename[:-4])).size().getInfo() == 0 # if not exist in S2 of GEE
            ]

pprint(fileList)


fileList = [
    # "S1B_IW_GRDH_1SDV_20210716T020155_20210716T020220_027813_0351A3_E556",
    "S1B_IW_GRDH_1SDV_20210716T020220_20210716T020245_027813_0351A3_0B43.tif",
    "S1B_IW_GRDH_1SDV_20210716T020245_20210716T020310_027813_0351A3_29DF.tif"
]

upload_flag = True

""" To COG GeoTiff """
if upload_flag:

    for filename in fileList:
        print()
        print(filename)
        print("---------------------------------------------------------")

        src_url = dataPath / filename
        dst_url = savePath / filename
        os.system(f"gdal_translate {src_url} {dst_url} -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW")

    """ Upload COG into GCS """
    os.system(f"gsutil -m cp -r {savePath}/* {gs_dir}")
    os.rmdir(savePath) # delete cog folder after uploading.

    """ Upload to earth engine asset """
    for filename in fileList:
        print(f"\n{filename[:-4]}")

        asset_id = f"users/omegazhangpzh/Sentinel1/{filename[:-4]}"
        os.system(f"earthengine upload image --asset_id={asset_id} {gs_dir}/{filename}")



""" Set Properties """
