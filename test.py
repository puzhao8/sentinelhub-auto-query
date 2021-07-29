
import os
import time
from pathlib import Path

# input_folder = Path("D:\Sentinel_Hub\data\S1_GRD")
# fileList = [
#             "S1A_IW_GRDH_1SDV_20210727T021109_20210727T021138_038957_0498BA_C633",
#             "S1B_IW_GRDH_1SDV_20210726T141029_20210726T141058_027966_03562E_EA63",
#             "S1B_IW_GRDH_1SDV_20210726T141058_20210726T141123_027966_03562E_2654",
#             "S1B_IW_GRDH_1SDV_20210726T141123_20210726T141148_027966_03562E_F0A3",
#             "S1B_IW_GRDH_1SDV_20210726T141148_20210726T141213_027966_03562E_A8B5",
#             "S1B_IW_GRDH_1SDV_20210726T141213_20210726T141238_027966_03562E_8CCD",
#             "S1B_IW_GRDH_1SDV_20210727T012057_20210727T012122_027973_035661_77CD",
#             "S1B_IW_GRDH_1SDV_20210727T012122_20210727T012147_027973_035661_6C12",
#             "S1B_IW_GRDH_1SDV_20210727T012147_20210727T012212_027973_035661_CAEF",
#             "S1B_IW_GRDH_1SDV_20210727T012212_20210727T012237_027973_035661_5EE2",
#             "S1B_IW_GRDH_1SDV_20210727T012237_20210727T012302_027973_035661_9E41",
#             "S1B_IW_GRDH_1SDV_20210727T012302_20210727T012335_027973_035661_73F2"
#         ]

# TASK_DICT = {}
# fileListCopy = fileList.copy()
# while (len(fileListCopy) > 0):
#     time.sleep(10)
#     print("\n----------------------------- while -------------------------------")  

#     for filename in fileList:            
#         input_url = input_folder / f"{filename}.zip"
#         if (os.path.exists(input_url)) and (filename not in TASK_DICT.keys()):

#             print("\n\n\n")    
#             print(filename)
#             print("-------------------------------------------------------")

#             # output_url = output_folder / f"{filename}.tif"

#             # if not os.path.exists(str(output_url)):
#             #     S1_GRD_Preprocessing(graph, input_url, output_url)

#             # # convert into cloud-optimized geotiff
#             # cog_url = cog_folder / f"{filename}.tif"
#             # os.system(f"gdal_translate {output_url} {cog_url} -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW")

#             # # """ Upload COG into GCS """
#             # os.system(f"gsutil -m cp -r {cog_url} {gs_dir}/")

#             # task_dict = upload_cog_into_eeImgCol(output_folder, gs_dir, fileList=[filename], upload_flag=True, eeUser=eeUser)
#             TASK_DICT.update({filename: filename})
            
#             try:
#                 fileListCopy.remove(filename) # remove item from list after finishing uploading
#                 print(f"{filename}: [removed!]")
#             except:
#                 print(f"{filename}: [failed to remove!]")
            
#             # pprint(TASK_DICT)
#             # upload_finish_flag = check_status_and_set_property(TASK_DICT, query_info)
        
#         else:
#             print(f"{filename} [not existed!]")



dataPath = Path("D:\Sentinel_Hub\data\Tim")
src_url = dataPath / "S2_L2A_20210728_Mosaic.tif"
dst_url = dataPath / "S2_L2A_20210728_Mosaic_COG.tif"
os.system(f"gdal_translate {src_url} {dst_url} -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW")


