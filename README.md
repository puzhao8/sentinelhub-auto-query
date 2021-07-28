"# sentinelhub-auto-query" 

# Config Environment
## 1. Install anaconda

## 2. Install ESA SNAP Desktop Software 


### 2.1 config snappy (ESA SNAP python library)
snappy only supports python 2.7 and python 3.6 (python 3.6 is recommended.)
https://senbox.atlassian.net/wiki/spaces/SNAP/pages/50855941/Configure+Python+to+use+the+SNAP-Python+snappy+interface

### 2.2 for windows
$ cd C:\SNAP\bin
$ snap-conf C:\Anaconda3\envs\snap\python G:\PyProjects\sentinelhub-auto-query\outputs\

copy generated snappy folder into envs you would like to use:
C:\Anaconda3\envs\snap\Lib\site-packages\

## 3. Install denpendencies
### export env (for export only)
```
conda env export -f env.yml --no-builds
```

### config python environment from yml
```
conda env update --file env.yml --prune
```

## 4. gcloud insallation and initializing
https://cloud.google.com/sdk/docs/install
https://cloud.google.com/sdk/docs/initializing

``` bash
gcloud init
gcloud auth login
gcloud config set project [project-name]
```


# How to run:
``` bash 
python main_run_multi_scripts.py 
```

This command line will run sentinel_query_download.py and update_sentinel_for_gee.py at the same time, and you need to choose the satellite you would like to download and process.
``` python
from config.sentinel1 import cfg
from config.sentinel2 import cfg
```
In the config folder, you can set parameters.


