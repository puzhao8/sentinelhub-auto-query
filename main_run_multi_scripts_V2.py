import os                                                                       
from multiprocessing import Pool   
from prettyprinter import pprint   
from easydict import EasyDict as edict                                          
                                                                                                                                                                                                                                                                                             

if __name__ == "__main__":
    cfg = edict({
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

    })

    from Step1_S1_GRD_auto_query import query_sentinel_data, download_sentinel_data
    from main_product_wise_auto_upload import sentinel_preprocessing_and_upload

    query_info = query_sentinel_data(cfg)

    def prcess1():
        download_sentinel_data(query_info)

    def process2():
        sentinel_preprocessing_and_upload(query_info)

    processes = ('prcess1()', 
                'process2()')

    # download_sentinel_data(query_info)
    # sentinel_preprocessing_and_upload(query_info)


    def run_process(process):                                                             
        eval(process)                                       
                                                                                    
    pool = Pool(processes=len(processes)) 
    pool.map(run_process, processes)
