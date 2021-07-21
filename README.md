"# sentinelhub-auto-query" 

# export env
conda env export -f env.yml --no-builds
conda env update --file env.yml --prune

# Linux Subsystems
C:\Users\omega\AppData\Local\Packages\CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc\LocalState\rootfs

http://mmb.irbbarcelona.org/molywood/tutorials/windows_sub, https://repo.anaconda.com/archive/

https://www.howtogeek.com/261383/how-to-access-your-ubuntu-bash-files-in-windows-and-your-windows-system-drive-in-bash/




# config snappy (support python 2.7 and python 3.6)
## tutorial on how to config 
https://senbox.atlassian.net/wiki/spaces/SNAP/pages/50855941/Configure+Python+to+use+the+SNAP-Python+snappy+interface

$ cd C:\SNAP\bin
$ snap-conf C:\Anaconda3\envs\snap\python G:\PyProjects\sentinelhub-auto-query\outputs\

copy generated snappy folder into envs you would like to use:
C:\Anaconda3\envs\snap\Lib\site-packages\
