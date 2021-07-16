
import os
from pathlib import Path
from prettyprinter import pprint
from snappy import jpy, ProgressMonitor, ProductIO
# from read_all_folders import read_all_folders_in


FileReader = jpy.get_type('java.io.FileReader')
GraphIO = jpy.get_type('org.esa.snap.core.gpf.graph.GraphIO')
Graph = jpy.get_type('org.esa.snap.core.gpf.graph.Graph')
GraphProcessor = jpy.get_type('org.esa.snap.core.gpf.graph.GraphProcessor')
PrintPM = jpy.get_type('com.bc.ceres.core.PrintWriterProgressMonitor')

""" S1_GRD_Preprocessing """
def S1_GRD_Preprocessing(graphFile, input_url, output_url):
    ### Load Graph
    graph = GraphIO.read(graphFile)

    input_url = str(input_url)
    output_url = str(output_url)

    graph.getNode("read").getConfiguration().getChild(0).setValue(input_url)
    graph.getNode("write").getConfiguration().getChild(0).setValue(output_url)


    ### Execute Graph
    GraphProc = GraphProcessor()

    ### or a more concise implementation
    ConcisePM = jpy.get_type('com.bc.ceres.core.PrintWriterConciseProgressMonitor')
    System = jpy.get_type('java.lang.System')
    pm = PrintPM(System.out)
    # ProductIO.writeProduct(resultProduct, outPath, "NetCDF-CF", pm)

    # GraphProcessor.executeGraph(graph, ProgressMonitor.NULL)
    GraphProc.executeGraph(graph, pm)
    # GraphProcessor.executeGraph(graph)

""" batch_S1_GRD_processing """
def batch_S1_GRD_processing(input_folder, output_folder):

    for filename in os.listdir(str(input_folder)):

        # if filename[:-4] == ".zip":
        print("\n\n\n")    
        print(filename)
        print("-------------------------------------------------------\n")

        input_url = input_folder / filename.replace(".tif", ".zip")
        output_url = output_folder / (filename.split(".")[0] + ".tif")

        if not os.path.exists(str(output_url)):
            S1_GRD_Preprocessing(graphFile, input_url, output_url)
    

""" upload_cog_as_eeImgCol """
def upload_cog_as_eeImgCol(dataPath, gs_dir, upload_flag=True):
    savePath = dataPath / "COG"
    if not os.path.exists(savePath): os.makedirs(savePath)

    # S1 = ee.ImageCollection("COPERNICUS/S1_GRD")
    # S2 = ee.ImageCollection("COPERNICUS/S2")

    fileList = [filename for filename in os.listdir(dataPath) 
                    if (".tif" in filename) # this product doesn't exist in GEE
                        # and S1.filter(ee.Filter.eq("system:index", filename[:-4])).size().getInfo() == 0 # if not exist in S1 of GEE
                        # and S2.filter(ee.Filter.eq("PRODUCT_ID", filename[:-4])).size().getInfo() == 0 # if not exist in S2 of GEE
                ]

    pprint(fileList)

    """ To COG GeoTiff """
    if upload_flag:
        for filename in fileList:
            print(filename)

            src_url = dataPath / filename
            dst_url = savePath / filename
            os.system(f"gdal_translate {src_url} {dst_url} -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW")

    
        """ Upload COG into GCS """
        os.system(f"gsutil -m cp -r {savePath}/* {gs_dir}")

        """ Upload to earth engine asset """
        for filename in fileList:
            print(f"\n{filename[:-4]}")
            asset_id = f"users/omegazhangpzh/Sentinel1/{filename[:-4]}"
            os.system(f"earthengine upload image --asset_id={asset_id} {gs_dir}/{filename}")



    """ Set Properties """



if __name__ == "__main__":

    ### update input and output url
    graphFile = FileReader("G:\PyProjects\sentinelhub-auto-query\graphs\S1_GRD_preprocessing_GEE.xml")
    input_folder = Path("G:/PyProjects/sentinelhub-auto-query/data/S1_GRD_0716")
    output_folder = Path("G:/PyProjects/sentinelhub-auto-query/outputs/S1_GRD_0716")
    gs_dir = "gs://wildfire-nrt/Sentinel1/"

    batch_S1_GRD_processing(input_folder, output_folder)
    upload_cog_as_eeImgCol(output_folder, gs_dir, upload_flag=True)



