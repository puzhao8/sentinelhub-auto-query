"# sentinelhub-auto-query" 

# Install anaconda 

# config snappy (ESA SNAP python library)
## snappy only supports python 2.7 and python 3.6 (python 3.6 is recommended.)
https://senbox.atlassian.net/wiki/spaces/SNAP/pages/50855941/Configure+Python+to+use+the+SNAP-Python+snappy+interface

## for windows
$ cd C:\SNAP\bin
$ snap-conf C:\Anaconda3\envs\snap\python G:\PyProjects\sentinelhub-auto-query\outputs\

copy generated snappy folder into envs you would like to use:
C:\Anaconda3\envs\snap\Lib\site-packages\

# Install denpendencies
## export env (for export only)
conda env export -f env.yml --no-builds

## config python environment from yml
conda env update --file env.yml --prune

# gcloud insallation and initializing
https://cloud.google.com/sdk/docs/install
https://cloud.google.com/sdk/docs/initializing

gcloud init
gcloud auth login
<!-- gcloud config set project ee-globalchange-gee4geo -->
gcloud config set project nrt-wildfire-monitoring



