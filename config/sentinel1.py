cfg = {
        # query parameters
        "roi_url": "inputs/BC_ROIs.geojson",

        "platformname": "Sentinel-1", # Sentinel-2
        "producttype": 'GRD', # S2MSI1C, S2MSI2A

        "start_date": None,
        "end_date": None,

        # download parameters
        "download_flag": True,
        "datafolder": "D:/Sentinel_Hub", # where to save data


        # upload parameters
        "eeUser": "omegazhangpzh",
        "gs_dir": "gs://sar4wildfire/Sentinel1",
        "graph_url": "G:\PyProjects\sentinelhub-auto-query\graphs\S1_GRD_preprocessing_GEE.xml"

    }