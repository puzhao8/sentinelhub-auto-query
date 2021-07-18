

import os, subprocess
from prettyprinter import pprint

# eeUser = "omegazhangpzh"
# gs_dir = "gs://wildfire-nrt/Sentinel1"

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