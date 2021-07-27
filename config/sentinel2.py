cfg = {
        # query parameters
        "roi_url": "inputs/BC_ROIs.geojson",

        "platformname": "Sentinel-2", # Sentinel-2
        "producttype": 'S2MSI1C', # S2MSI1C, S2MSI2A
        "cloudcoverpercentage": 50, # 0-100

        "start_date": "2021-07-25", #"2021-07-20",
        "end_date": "2021-07-26", #"2021-07-22",

        # download parameters
        "download_flag": True,
        "datafolder": "D:/Sentinel_Hub", # where to save data

        # upload parameters
        "eeUser": "omegazhangpzh",
        "gs_dir": "gs://sar4wildfire/Sentinel2",
        "graph_url": "G:\PyProjects\sentinelhub-auto-query\graphs\S2_resamping_graph.xml"
    }