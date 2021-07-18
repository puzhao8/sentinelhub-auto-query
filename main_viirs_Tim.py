# https://git.earthdata.nasa.gov/projects/LPDUR
# wavelength: https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/viirs/
# viirs ftp: https://e4ftl01.cr.usgs.gov/VIIRS/VNP09GA.001/2021.07.05/
# https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP09GA/
# hHHvVV GRID: https://modis-land.gsfc.nasa.gov/MODLAND_grid.html
import datetime
import datetime as dt
from glob import glob
from pathlib import Path

import h5py
import numpy as np
import os
from osgeo import gdal, gdal_array

def get_geoInfo_and_projection(f):
    
    fileMetadata = f['HDFEOS INFORMATION']['StructMetadata.0'][()].split()   # Read file metadata
    fileMetadata = [m.decode('utf-8') for m in fileMetadata]                 # Clean up file metadata
    # fileMetadata[0:33]                                                       # Print a subset of the entire file metadata record

    ulc = [i for i in fileMetadata if 'UpperLeftPointMtrs' in i][0]    # Search file metadata for the upper left corner of the file
    ulcLon = float(ulc.split('=(')[-1].replace(')', '').split(',')[0]) # Parse metadata string for upper left corner lon value
    ulcLat = float(ulc.split('=(')[-1].replace(')', '').split(',')[1]) # Parse metadata string for upper left corner lat value

    yRes, xRes = -926.6254330555555,  926.6254330555555 # Define the x and y resolution
    # yRes, xRes = -500,  500 # Define the x and y resolution

    '''Currently, VIIRS HDF-EOS5 files do not contain information regarding the spatial resolution of the dataset within.'''
    # if nRow == 1200:                      # VIIRS A1 - 1km or 1000m
    #     yRes = -926.6254330555555    
    #     xRes = 926.6254330555555
    # elif nRow == 2400:                    # VIIRS H1 - 500m
    #     yRes = -463.31271652777775
    #     xRes = 463.31271652777775
    # elif nRow == 3600 and nCol == 7200:    # VIIRS CMG
    #     yRes = -0.05
    #     xRes = 0.05
    #     # Re-set upper left dims for CMG product                
    #     ulcLon = -180.00
    #     ulcLat = 90.00

    geoInfo = (ulcLon, xRes, 0, ulcLat, 0, yRes)        # Define geotransform parameters

    prj = 'PROJCS["Sphere_Sinusoidal",\
        GEOGCS["GCS_Sphere",\
            DATUM["Not_specified_based_on_Authalic_Sphere",\
                SPHEROID["Sphere",6371000,0]],\
            PRIMEM["Greenwich",0],\
            UNIT["Degree",0.017453292519943295]],\
        PROJECTION["Sinusoidal"],\
        PARAMETER["False_Easting",0],\
        PARAMETER["False_Northing",0],\
        PARAMETER["Central_Meridian",0],\
        UNIT["Meter",1],\
        AUTHORITY["EPSG","53008"]]'

    projInfo = {'SINU':'PROJCS["unnamed",GEOGCS["Unknown datum based upon the custom spheroid", DATUM["Not specified (based on custom spheroid)", SPHEROID["Custom spheroid",6371007.181,0]],PRIMEM["Greenwich",0], UNIT["degree",0.0174532925199433]], PROJECTION["Sinusoidal"],PARAMETER["longitude_of_center",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["Meter",1]]',
            'GEO':'GEOGCS["Unknown datum based upon the Clarke 1866 ellipsoid", DATUM["Not specified (based on Clarke 1866 spheroid)", SPHEROID["Clarke 1866",6378206.4,294.9786982139006]], PRIMEM["Greenwich",0], UNIT["degree",0.0174532925199433]]'}

    return geoInfo, prj

def convert_h5_to_cog(inDir, outDir, BANDS=["M3", "M4", "M5", "M7", "M10", "M11", "QF2"], band_scale_flag=False):
    # os.chdir(inDir)   
    # VNP = Path(os.path.split(inDir)[0])                                                      # Change to working directory
    
    # outDir = Path(os.path.split(VNP)[0]) / 'COG' # Set output directory
    
    print("BADNS: ", BANDS)
    if not os.path.exists(outDir): os.makedirs(outDir)                      # Create output directory


    fileList = [file for file in os.listdir(inDir) if file.endswith('.h5') and file.startswith('VNP09GA')] # Search for .h5 files in current directory
    
    print("------------------------------------")
    for f in fileList: print(f)       
    print("------------------------------------")                                                                # Print files in list

    date = [] # Create empty list to store dates of each file
    i = 0     # Set up iterator for automation in cell block below

    for t in fileList:
        print(f"\n----> {t} <----")

        yeardoy = t.split('.')[1][1:]                                                                  # Split name,retrieve ob date
        outName = t.rsplit('.', 1)[0]                                                                  # Keep filename for outname
        date1 = dt.datetime.strptime(yeardoy,'%Y%j').strftime('%m/%d/%Y')                              # Convert date
        date.append(date1)                                                                             # Append to list of dates
        f = h5py.File(os.path.normpath(Path(inDir) / t), "r")                                                             # Read in VIIRS HDF-EOS5 file
        
        # geoInfo and Projection
        geoInfo, prj = get_geoInfo_and_projection(f)

        h5_objs = []                                                                                   # Create empty list
        f.visit(h5_objs.append)                                                                        # Retrieve obj append to list
        
        # Search for SDS with 1km or 500m grid
        grids = list(f['HDFEOS']['GRIDS']) # List contents of GRIDS directory                                      # Clean up file metadata
    

        allSDS = [o for grid in grids for o in h5_objs if isinstance(f[o],h5py.Dataset) and grid in o] # Create list of SDS in file
        
        r = f[[a for a in allSDS if 'M5' in a][0]] 
        scaleFactor = r.attrs['Scale'][0]    # Set scale factor to a variable
        fillValue = r.attrs['_FillValue'][0] # Set fill value to a variable  

        print(f"scaleFactor: {scaleFactor}")

        band_dict = {}
        for band_name in BANDS:
            # print(band_name)
            band = f[[a for a in allSDS if band_name in a][0]][()]   
                                                             # Open SDS M5 = Red
            if band_scale_flag and ('QF' not in band_name):
                band = band * scaleFactor

            band_dict[band_name] = band                                                   

        data = np.dstack(tuple(band_dict.values()))
        print(data.shape)

        data[data == fillValue * scaleFactor] = 0 # Set fill value equal to nan
        
        # qf = f[[a for a in allSDS if 'QF5' in a][0]][()]                                               # Import QF5 SDS
        # qf2 = f[[a for a in allSDS if 'QF2' in a][0]][()]                                              # Import QF2 SDS                                                                  # Append to list
        
        params = {
                'all':{'data':data, 'band': 'all'}
            }
        for p in params:
            try: 
                data = params[p]['data']                                                               # Define array to be exported
                data[data.mask == True] = fillValue                                                    # Masked values = fill value
            except: AttributeError

            # outputName = os.path.normpath('{}{}.tif'.format(outDir, outName))    # Generate output filename
            outputName = str(outDir / f"{outName}.tif")   # Generate output filename

            nRow, nCol = data.shape[0], data.shape[1]                                                  # Define row/col from array
            dataType = gdal_array.NumericTypeCodeToGDALTypeCode(data.dtype)                            # Define output data type
            driver = gdal.GetDriverByName('GTiff')                                                     # Select GDAL GeoTIFF driver
                                                                        # Diff for exporting RGBs
            data = params[p]['data']                                                               # Define the array to export
            dataType = gdal_array.NumericTypeCodeToGDALTypeCode(data.dtype)                        # Define output data type
            options = [
                        # 'PHOTOMETRIC=RGB', 
                        # 'PROFILE=GeoTIFF'
                        "TILED=YES",
                        "COMPRESS=LZW",
                        "INTERLEAVE=BAND"]                                       # Set options to RGB TIFF
            outFile = driver.Create(outputName, nCol, nRow, len(BANDS), dataType, options=options)          # Specify parameters of GTIFF
            
            for idx, band in enumerate(BANDS):  
                print(idx, band)                                                       # loop through each band (3)
                rb = outFile.GetRasterBand(idx+1)
                rb.WriteArray(data[..., idx])                                  # Write to output bands 1-3
                # rb.SetNoDataValue(1.1)                                       # Set fill val for each band
                # rb.SetDescription(band)
                rb = None
                
            outFile.SetGeoTransform(geoInfo)                                                           # Set Geotransform
            outFile.SetProjection(prj)                                                                 # Set projection
            outFile = None                                                                             # Close file

        print('Processed file: {} of {}'.format(i+1, len(fileList)))                                    # Print the progress
        i += 1

def crs_cloud_optimization(file):
    input_raster = gdal.Open(file)
    raster_name = os.path.split(file)[1]
    output_dir_crs = os.path.split(file)[0] + "/crs_optimized/" + raster_name
    warp = gdal.Warp(output_dir_crs, input_raster, dstSRS='EPSG:4326', dstNodata=0)
    warp.GetRasterBand(1).SetNoDataValue(0)
    warp = None

    # cloud optimized tif
    src_url = output_dir_crs
    dst_url = os.path.split(file)[0] + "/COG/" + 'VNP09GA' + raster_name[-22:-15] + '.tif'
    os.system(f"gdal_translate {src_url} {dst_url} -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW")

if __name__ == "__main__":
    # # 1km vs. 500m --> "M5", "M7", "M10" vs. "I1", "I2", "I3"
    # # 500m: "M3",     "M4",  "I1",  "I2",   "I3",    "M11",  "QF2"
    # # 1km:  "M3",     "M4",  "M5",  "M7",   "M10",    "M11",  "QF2"
    # # "Blue", "Green", "Red", "NIR", "SWIR1", "SWIR2", "BitMask"
    # BANDS = ["M3",     "M4",  "M5",  "M7",   "M10",    "M11",  "QF2"]

    # Download from Lance
    lance_date = datetime.date.today() - datetime.date(2021, 1, 1)
    lance_date = lance_date.days
    print(lance_date)
    command = "c:/wget/wget.exe -e robots=off -m -np -R .html,.tmp -nH --cut-dirs=5 " + f"\"https://nrt4.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/5000/VNP09GA_NRT/2021/{lance_date}/VNP09GA_NRT.A2021{lance_date}.h10v03.001.h5\" --header \"Authorization: Bearer emhhb3l1dGltOmVtaGhiM2wxZEdsdFFHZHRZV2xzTG1OdmJRPT06MTYyNjQ0MTQyMTphMzhkYTcwMzc5NTg1M2NhY2QzYjY2NTU0ZWFkNzFjMGEwMTljMmJj\" -P nasa-viirs/VNP09GA"

    os.system(command)

    # # CRS optimization and cloud optimization
    # for file in glob('COG/*/*/*.tif'):
    #     os.remove(file)
    # dataPath = Path('nasa-viirs')
    # for date in os.listdir(dataPath):

    #     outDir = Path(os.path.split(dataPath)[0]) / 'COG' / date
    #     print(f"outDir: {outDir}")

    #     convert_h5_to_cog(inDir=dataPath / date, outDir=outDir, BANDS=["M3", "M4", "M5", "M7", "M10", "M11", "QF2"])

    # # upload to Gcloud
    # optdatalist = glob('COG/VNP09GA/*.tif')
    # for file in optdatalist:
    #     crs_cloud_optimization(file)
    # gs_dir = "gs://eo4wildfire/VIIRS/"
    # os.system(f"gsutil -m cp -r COG/VNP09GA/COG/* {gs_dir}")

    # # upload from Gcloud to GEE
    # gs_dir = "gs://eo4wildfire/VIIRS/"
    # uploaddatalist = glob('COG/VNP09GA/COG/*.tif')
    # for filename in uploaddatalist:
    #     date = datetime.date(2021, 1, 1) + datetime.timedelta(int(os.path.split(filename)[1][-7:-4]))
    #     # os.system(f"earthengine upload image --asset_id=users/zhaoyutim/VNP09GA/{os.path.split(filename)[1][:-4]} {gs_dir+os.path.split(filename)[1]}")
    #     os.system(f'earthengine asset set --time_start {str(date)} users/zhaoyutim/VNP09GA/{os.path.split(filename)[1][:-4]}')