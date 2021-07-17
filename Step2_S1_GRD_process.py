import snappy
import os
from pathlib import Path
from snappy import jpy, ProgressMonitor, ProductIO
# from read_all_folders import read_all_folders_in


FileReader = jpy.get_type('java.io.FileReader')
GraphIO = jpy.get_type('org.esa.snap.core.gpf.graph.GraphIO')
Graph = jpy.get_type('org.esa.snap.core.gpf.graph.Graph')
GraphProcessor = jpy.get_type('org.esa.snap.core.gpf.graph.GraphProcessor')
PrintPM = jpy.get_type('com.bc.ceres.core.PrintWriterProgressMonitor')


### Load Graph
graphFile = FileReader("G:\PyProjects\sentinelhub-auto-query\graphs\S1_GRD_preprocessing_GEE.xml")
graph = GraphIO.read(graphFile)

### update input and output url
input_folder = Path("G:/PyProjects/sentinelhub-auto-query/data/S1_GRD_0716")
output_folder = Path("G:/PyProjects/sentinelhub-auto-query/outputs/S1_GRD_0716")

def S1_GRD_Preprocessing(graph, input_url, output_url):
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

# fileList = [
#     "S1B_IW_GRDH_1SDV_20210714T141147_20210714T141212_027791_035101_0B6B.tif",
#     "S1B_IW_GRDH_1SDV_20210714T141212_20210714T141237_027791_035101_2BF8.tif"]

# for filename in fileList:
for filename in os.listdir(str(input_folder)):

    # if filename[:-4] == ".zip":
    print("\n\n\n")    
    print(filename)
    print("-------------------------------------------------------\n")

    input_url = input_folder / filename.replace(".tif", ".zip")
    output_url = output_folder / (filename.split(".")[0] + ".tif")

    if not os.path.exists(str(output_url)):
        S1_GRD_Preprocessing(graph, input_url, output_url)
    else: 
        print("alread processed!")


