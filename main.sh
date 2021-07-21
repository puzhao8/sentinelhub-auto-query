

conda activate ee
python3 update_viirs_nrt.py &
conda activate snap
python3 Step1_S1_GRD_auto_query.py

export PATH=/mnt/c/Anaconda3/condabin:$PATH

export PATH=/home/puzhao/anaconda3/bin:$PATH