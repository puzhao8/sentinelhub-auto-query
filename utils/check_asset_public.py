import os, json
import subprocess
from easydict import EasyDict as edict

def check_asset_permission(asset_id):
    response = subprocess.getstatusoutput(f"earthengine acl get {asset_id}")[1]
    res_dict = edict(json.loads(response))

    if 'all_users_can_read' in res_dict:
        print(f"{asset_id}: {res_dict.all_users_can_read}")
        return res_dict.all_users_can_read
    else: 
        print(f"{asset_id}: {False}")
        return False


if __name__ == "__main__":

    NRT_AF = subprocess.getstatusoutput("earthengine ls users/omegazhangpzh/NRT_AF/")
    asset_list = NRT_AF[1].replace("projects/earthengine-legacy/assets/", "").split("\n")
    # asset_list = [asset_id for asset_id in asset_list if asset_id.split("_")[-1] in ['24h']]

    print("all_users_can_read: True or False")
    for asset_id in asset_list:

        # print("\n------------------------------")
        # print(f"{asset_id}")

        public_flag = check_asset_permission(asset_id)
        
        if not public_flag:
            print(f"earthengine acl set public {asset_id}")
            os.system(f"earthengine acl set public {asset_id}")
            # pass
        

    
    