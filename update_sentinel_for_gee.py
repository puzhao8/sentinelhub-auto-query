

from logging import exception
import os, datetime, subprocess, time, json
import glob
from pathlib import Path
from httplib2 import Response
from prettyprinter import pprint
from snappy import jpy, ProgressMonitor, ProductIO
# from read_all_folders import read_all_folders_in
from easydict import EasyDict as edict
from datetime import datetime

import ee
ee.Initialize()


FileReader = jpy.get_type('java.io.FileReader')
GraphIO = jpy.get_type('org.esa.snap.core.gpf.graph.GraphIO')
Graph = jpy.get_type('org.esa.snap.core.gpf.graph.Graph')
GraphProcessor = jpy.get_type('org.esa.snap.core.gpf.graph.GraphProcessor')
PrintPM = jpy.get_type('com.bc.ceres.core.PrintWriterProgressMonitor')

""" S1_GRD_Preprocessing """
def S1_GRD_Preprocessing(graph, input_url, output_url):
    ### Load Graph
    # graph = GraphIO.read(graphFile)

    input_url = str(input_url)
    output_url = str(output_url)

    graph.getNode("read").getConfiguration().getChild(0).setValue(input_url)
    graph.getNode("write").getConfiguration().getChild(0).setValue(output_url)


    ### Execute Graph
    GraphProc = GraphProcessor()

    ### or a more concise implementation
    # ConcisePM = jpy.get_type('com.bc.ceres.core.PrintWriterConciseProgressMonitor')
    System = jpy.get_type('java.lang.System')
    pm = PrintPM(System.out)
    # ProductIO.writeProduct(resultProduct, outPath, "NetCDF-CF", pm)

    # GraphProcessor.executeGraph(graph, ProgressMonitor.NULL)
    GraphProc.executeGraph(graph, pm)
    # GraphProcessor.executeGraph(graph)

""" batch_S1_GRD_processing """
def batch_S1_GRD_processing(input_folder, output_folder, fileList):
    if fileList is None: fileList = os.listdir(str(input_folder))
    for filename in fileList:

        # if filename[:-4] == ".zip":
        print("\n\n\n")    
        print(filename)
        print("-------------------------------------------------------\n")

        input_url = input_folder / filename.replace(".tif", ".zip")
        output_url = output_folder / (filename.split(".")[0] + ".tif")

        if not os.path.exists(str(output_url)):
            S1_GRD_Preprocessing(graph, input_url, output_url)
    


def load_json(url) -> edict:
    with open(url, 'r') as fp:
        data = edict(json.load(fp))
    return data


def set_image_property(asset_id, query_info):
    # json_folder = Path("G:/PyProjects/sentinelhub-auto-query/outputs/BC_ROI_2")
    # latest_json = sorted(os.listdir(json_folder))[-1]
    # json_url = json_folder / latest_json

    product_id = os.path.split(asset_id)[-1]
    product_info = query_info['products'][product_id]

    if 'S1' in product_id:
        time_start = datetime.strptime(product_id.split("_")[4], "%Y%m%dT%H%M%S").strftime("%Y-%m-%dT%H:%M:%S")
        time_end = datetime.strptime(product_id.split("_")[5], "%Y%m%dT%H%M%S").strftime("%Y-%m-%dT%H:%M:%S")
    
    if 'S2' in product_id:
        time_start = datetime.strptime(product_id.split("_")[2], "%Y%m%dT%H%M%S").strftime("%Y-%m-%dT%H:%M:%S")
        time_end = datetime.strptime(product_id.split("_")[-1], "%Y%m%dT%H%M%S").strftime("%Y-%m-%dT%H:%M:%S")

    # footprint = product_info['footprint']

    print()
    pprint(product_id)
    print("-----------------------------------------------------------------")
    print(time_start)
    # print(footprint)

    os.system(f"earthengine asset set --time_start {time_start} {asset_id}")
    os.system(f"earthengine asset set --time_end {time_end} {asset_id}")

    property_dict = {
        'relativeorbitnumber': 'relativeOrbitNumber_start',
        'orbitdirection': 'orbitProperties_pass',
    }

    for property in product_info.keys():
        value = product_info[property]

        if property in property_dict.keys(): property = property_dict[property]

        print(property, value)    
        os.system(f"earthengine asset set -p {property}={value} {asset_id}")

    os.system(f"earthengine asset set -p {'gee'}={'false'} {asset_id}")
    # os.system(f"earthengine asset set -p {'transmitterReceiverPolarisation'}={'[VH, VV]'} {asset_id}")


""" upload_cog_as_eeImgCol """
def upload_cog_into_eeImgCol(dataPath, gs_dir, fileList=None, upload_flag=True, eeUser="omegazhangpzh"):
    cogPath = dataPath / "COG"

    # eeUser = "omegazhangpzh"
    eeImgCol_name = os.path.split(gs_dir)[-1]
    # print(os.path.split(gs_dir))
    eeImgCol = f"users/{eeUser}/{eeImgCol_name}"
    print(f"eeImgCol: {eeImgCol}")

    if not os.path.exists(cogPath): os.makedirs(cogPath)

    S1 = ee.ImageCollection("COPERNICUS/S1_GRD")
    S2 = ee.ImageCollection("COPERNICUS/S2")

    if fileList is None: fileList = [filename[:-4] for filename in os.listdir(dataPath) if (".tif" in filename)]
    fileList = [filename for filename in fileList
                    # if (".tif" in filename) # this product doesn't exist in GEE
                    if (S1.filter(ee.Filter.eq("system:index", filename)).size().getInfo() == 0 # if not exist in S1 of GEE
                        and S2.filter(ee.Filter.eq("PRODUCT_ID", filename)).size().getInfo() == 0 # if not exist in S2 of GEE
                    )
                ]

    pprint(fileList)

    """ To COG GeoTiff """
    if upload_flag:

        """ Upload to earth engine asset """
        task_dict = {}
        for filename in fileList:
            print(f"\n{filename}")
            print("--------------------------------------------------------------------")

            asset_id = f"{eeImgCol}/{filename}"
            ee_upload_image = f"earthengine upload image --force --asset_id={asset_id} {gs_dir}/{filename}.tif"

            ee_upload_response = subprocess.getstatusoutput(ee_upload_image)[1]
            task_id = ee_upload_response.split("ID: ")[-1]
            task_dict.update({filename: {'task_id': task_id, 'asset_id': asset_id}})

            print(f"{asset_id}")
            pprint(f"task id: {task_id}")
            print()

        return task_dict


def check_status_and_set_property(task_dict, query_info):
    # """ get property json """
    # json_folder = Path("G:/PyProjects/sentinelhub-auto-query/outputs/BC_ROIs")
    # latest_json = sorted(os.listdir(json_folder))[-1]
    # json_url = json_folder / latest_json

    # query_info = load_json(json_url)

    """ check upload status """
    print("=============> check upload status <===============")
    # upload_finish_flag = False
    # while(not upload_finish_flag):
    #     time.sleep(60) # delay 30s
        
    upload_finish_flag = True
    for filename in task_dict.keys():

        asset_id = task_dict[filename]['asset_id'] #f"users/omegazhangpzh/Sentinel1/{filename}"
        task_id = task_dict[filename]['task_id']

        check_upload_status = f"earthengine task info {task_id}"
        response = subprocess.getstatusoutput(check_upload_status)[1]
        state = response.split("\n")[1].split(": ")[-1]
        # state = edict(json.loads(response))['state']

        task_dict[filename].update({'state': state})

        if state == "COMPLETED":
            os.system(f"earthengine acl set public {asset_id}")

            # """ Set Properties """
            set_image_property(asset_id, query_info)
            # task_dict.pop(filename)

        else:
            upload_finish_flag = False

        # check_asset_permission(asset_id)
        print(f"\n{filename}: {state}")

    print("-----------------------------------------------------------------------\n")
    # pprint(task_dict)


    """ set image property """
    # # eeUser = "omegazhangpzh"
    # # gs_dir = "gs://wildfire-nrt/Sentinel1"

    # time.sleep(10) # wait?
    # imgCol_name = os.path.split(gs_dir)[-1]
    # response = subprocess.getstatusoutput(f"earthengine ls users/{eeUser}/{imgCol_name}")
    # asset_list = response[1].replace("projects/earthengine-legacy/assets/", "").split("\n")

    # for filename in task_dict.keys():
    #     asset_id = task_dict[filename]["asset_id"]
    #     if asset_id in asset_list:
    #         set_image_property(asset_id, query_info)
    #     else:
    #         print(f"{asset_id} [Not Ready in GEE!]")

    return upload_finish_flag


def sentinel_preprocessing_and_upload(cfg, query_info):
    # cfg.update(query_info.cfg) 
    cfg = query_info.cfg

    gs_dir = cfg.gs_dir
    eeUser = cfg.eeUser
    cfg.datafolder = Path(cfg.datafolder)

    # workPath = Path(os.getcwd()) # Project Folder
    ### update input and output url
    graphFile = FileReader(str(cfg.graph_url))
    graph = GraphIO.read(graphFile)
    
    input_folder = cfg.datafolder / "data" / cfg.sat_folder
    output_folder = cfg.datafolder / "outputs" / cfg.sat_folder 
    cog_folder = output_folder / "COG"
    if not os.path.exists(cog_folder): os.makedirs(cog_folder)

    """ get query info and property json """
    # json_folder = datafolder / "outputs" / "BC_ROIs"
    # json_url = sorted(glob.glob(str(json_folder / f"{folder}*.json")))[-1]
    # print("\njson: " + os.path.split(json_url)[-1])

    # query_info = load_json(json_url)
    fileList = query_info['results']['products_list']
    pprint(fileList)

    # fileList = [
    #     "S1A_IW_GRDH_1SDV_20210719T013906_20210719T013931_038840_04954C_9B58"
    #     # "S1A_IW_GRDH_1SDV_20210719T013931_20210719T013956_038840_04954C_27C5"
    # ]

    """ S1 GRD Preprocessing, 
        Convert to COG, 
        upload into GCS,
        upload as eeImgCol of GEE """
    # product wise processing and uploading, 
    # you don't need to wait for all data being downloaded.
    TASK_DICT = {}
    fileListCopy = fileList.copy()
    while (len(fileListCopy) > 0):
        time.sleep(10)
        print("\n----------------------------- while -------------------------------")  

        for filename in fileList:            
            input_url = input_folder / f"{filename}.zip"
            if (os.path.exists(input_url)) and (filename not in TASK_DICT.keys()):

                print("\n\n\n")    
                print(filename)
                print("-------------------------------------------------------\n")

                output_url = output_folder / f"{filename}.tif"

                if not os.path.exists(str(output_url)):
                    S1_GRD_Preprocessing(graph, input_url, output_url)

                # convert into cloud-optimized geotiff
                cog_url = cog_folder / f"{filename}.tif"
                os.system(f"gdal_translate {output_url} {cog_url} -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW")

                # """ Upload COG into GCS """
                os.system(f"gsutil -m cp -r {cog_url} {gs_dir}/")

                task_dict = upload_cog_into_eeImgCol(output_folder, gs_dir, fileList=[filename], upload_flag=True, eeUser=eeUser)
                TASK_DICT.update(task_dict)
                
                try:
                    fileListCopy.remove(filename) # remove item from list after finishing uploading
                    print(f"{filename}: [removed!]")
                except:
                    print(f"{filename}: [failed to remove!]")
                
                # pprint(TASK_DICT)
                upload_finish_flag = check_status_and_set_property(TASK_DICT, query_info)
            
            else:
                print(f"{filename} [not existed!]")



    """ Set Image Property """
    fileList = list(TASK_DICT.keys())
    fileListCopy = fileList.copy()
    imgCol_name = os.path.split(gs_dir)[-1]
    while(len(fileListCopy) > 0):
        # time.sleep(10) # wait?
        response = subprocess.getstatusoutput(f"earthengine ls users/{eeUser}/{imgCol_name}")
        asset_list = response[1].replace("projects/earthengine-legacy/assets/", "").split("\n")

        for filename in fileList:
            asset_id = f"users/{eeUser}/{imgCol_name}/" + filename

            if asset_id in asset_list:
                set_image_property(asset_id, query_info)
                try:
                    fileListCopy.remove(filename) # remove item from list after finishing uploading
                    print(f"{filename}: [removed!]")
                except:
                    print(f"{filename}: [failed to remove!]")
            else:
                print(f"{asset_id} [Not Ready in GEE!]")



if __name__ == "__main__":

    # cfg = edict({
    #     # query parameters
    #     "roi_url": "inputs/BC_ROIs.geojson",

    #     "platformname": "Sentinel-1", # Sentinel-2
    #     "producttype": 'GRD', # S2MSI1C, S2MSI2A

    #     "start_date": None,
    #     "end_date": None,

    #     # download parameters
    #     "download_flag": True,
    #     "datafolder": "D:/Sentinel_Hub", # where to save data


    #     # upload parameters
    #     "eeUser": "omegazhangpzh",
    #     "gs_dir": "gs://sar4wildfire/Sentinel1",
    #     "graph_url": "G:\PyProjects\sentinelhub-auto-query\graphs\S1_GRD_preprocessing_GEE.xml"

    # })

    # from config.sentinel1 import cfg
    from config.sentinel2 import cfg
    from sentinel_query_download import query_sentinel_data, download_sentinel_data

    cfg = edict(cfg)
    query_info = query_sentinel_data(cfg, save_json=False)
    # download_sentinel_data(query_info)
    sentinel_preprocessing_and_upload(cfg, query_info)
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # batch_S1_GRD_processing(input_folder, output_folder, fileList)
    # upload_cog_as_eeImgCol(output_folder, gs_dir, json_url, fileList=None, upload_flag=True, eeUser=eeUser)

    # TASK_DICT_COPY = TASK_DICT.copy()
    # while(len(TASK_DICT_COPY) > 0):

    #     time.sleep(10) # wait?
    #     imgCol_name = os.path.split(gs_dir)[-1]
    #     response = subprocess.getstatusoutput(f"earthengine ls users/{eeUser}/{imgCol_name}")
    #     asset_list = response[1].replace("projects/earthengine-legacy/assets/", "").split("\n")

    #     for filename in TASK_DICT.keys():
    #         asset_id = task_dict[filename]["asset_id"]
    #         if asset_id in asset_list:
    #             set_image_property(asset_id, query_info)

    #             TASK_DICT_COPY.pop(filename)
    #         else:
    #             print(f"{asset_id} [Not Ready in GEE!]")

