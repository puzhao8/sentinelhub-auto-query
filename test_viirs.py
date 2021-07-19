import os
from pathlib import Path 

workspace = Path(os.getcwd())
dataPath = workspace / 'data' / 'VIIRS'

command = "c:/wget/wget.exe -e robots=off -m -np -R .html,.tmp -nH --cut-dirs=5 " + \
            f"\"https://nrt4.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/5000/VNP09GA_NRT/2021/199/VNP09GA_NRT.A2021199.h10v03.001.h5\" \
                --header \"Authorization: Bearer emhhb3l1dGltOmVtaGhiM2wxZEdsdFFHZHRZV2xzTG1OdmJRPT06MTYyNjQ0MTQyMTphMzhkYTcwMzc5NTg1M2NhY2QzYjY2NTU0ZWFkNzFjMGEwMTljMmJj\" \
             -P {dataPath}"

os.system(command)