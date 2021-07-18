import os                                                                       
from multiprocessing import Pool                                                
                                                                                                                                                                                                                                                                                             
def run_process(process):                                                             
    os.system('python {}'.format(process))                                       
                                                                                

# independent processes
processes = ('Step1_S1_GRD_auto_query.py', 
             'main_product_wise_auto_upload.py')

# dependent processes
other = ()

pool = Pool(processes=len(processes)+len(other)) 
pool.map(run_process, processes)
pool.map(run_process, other)
