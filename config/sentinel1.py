cfg = {
        # query parameters
        "roi_url": "inputs/BC_ROIs.geojson",
        # "roi_url": "inputs/US_S1_Query_ROI.geojson",

        "platformname": "Sentinel-1", # Sentinel-2
        "producttype": 'GRD', # S2MSI1C, S2MSI2A

        # "start_date": "2017-07-25", # None for the day before today
        # "end_date": "2017-07-29", # None for the day after today

        "start_date": None, # None for the day before today
        "end_date": None, # None for the day after today

        # download parameters
        "download_flag": True,
        "datafolder": "D:/Sentinel_Hub", # where to save data

        # upload parameters
        "eeUser": "omegazhangpzh",
        "gs_dir": "gs://sar4wildfire/Sentinel1",
        "graph_url": "graphs/S1_GRD_preprocessing_GEE.xml"
    }