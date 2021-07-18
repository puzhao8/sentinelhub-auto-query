

import os, subprocess
from prettyprinter import pprint

eeUser = "omegazhangpzh"
gs_dir = "gs://wildfire-nrt/Sentinel1"

# imgCol_name = os.path.split(gs_dir)[-1]
# response = subprocess.getstatusoutput(f"earthengine ls users/{eeUser}/{imgCol_name}")
# asset_list = response[1].replace("projects/earthengine-legacy/assets/", "").split("\n")

# pprint(asset_list)



footprint = {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [
                                -122.563354,
                                48.427082
                            ],
                            [
                                -119.180817,
                                48.817978
                            ],
                            [
                                -119.565086,
                                50.559021
                            ],
                            [
                                -123.068634,
                                50.167595
                            ],
                            [
                                -122.563354,
                                48.427082
                            ]
                        ]
                    ]
                ]
            }

property  = "geometry"
# os.system(f"earthengine asset set -p {property}={footprint['coordinates']} users/omegazhangpzh/Sentinel1/S1A_IW_GRDH_1SDV_20210717T015439_20210717T015508_038811_049457_C366")
os.system(f"earthengine asset set --footprint {footprint} users/omegazhangpzh/Sentinel1/S1A_IW_GRDH_1SDV_20210717T015439_20210717T015508_038811_049457_C366")


fileList = [
    "S1A_IW_GRDH_1SDV_20210717T015439_20210717T015508_038811_049457_C366",
    "S1A_IW_GRDH_1SDV_20210717T015508_20210717T015533_038811_049457_D2C7",
    "S1A_IW_GRDH_1SDV_20210717T015533_20210717T015558_038811_049457_CDE0",
    "S1A_IW_GRDH_1SDV_20210717T015623_20210717T015648_038811_049457_A51B",
    "S1A_IW_GRDH_1SDV_20210717T015648_20210717T015705_038811_049457_15E0",
    "S1B_IW_GRDH_1SDV_20210717T143444_20210717T143509_027835_03524A_B44E",
    "S1B_IW_GRDH_1SDV_20210717T143509_20210717T143534_027835_03524A_710C",
    "S1B_IW_GRDH_1SDV_20210717T143534_20210717T143559_027835_03524A_A482",
    "S1B_IW_GRDH_1SDV_20210717T143559_20210717T143624_027835_03524A_91F9",
    "S1B_IW_GRDH_1SDV_20210717T143624_20210717T143649_027835_03524A_53E6",
    "S1B_IW_GRDH_1SDV_20210717T143649_20210717T143714_027835_03524A_1BD2",
    "S1B_IW_GRDH_1SDV_20210717T143714_20210717T143739_027835_03524A_94D7"
]

# time.sleep(10) # wait?
imgCol_name = os.path.split(gs_dir)[-1]
response = subprocess.getstatusoutput(f"earthengine ls users/{eeUser}/{imgCol_name}")
asset_list = response[1].replace("projects/earthengine-legacy/assets/", "").split("\n")


cnt = 0
while(len(fileList) > 0):

    print(f"cnt: {cnt}")
        
    for filename in fileList:
        asset_id = f"users/{eeUser}/{imgCol_name}/{filename}"

        if asset_id in asset_list:
            # set_image_property(asset_id, query_info)

            fileList.remove(filename)

            pprint(len(fileList))
            pprint(fileList)

        else:
            print(f"{asset_id} [Not Ready in GEE!]")

    
    cnt = cnt + 1