
import time
import sys

sys.path.append(r"../src")

from signals import Signals
from imu.imu_handler import ImuHandler

imu = ImuHandler()

#imu.calibrate_imu_data()

while True:
    # Left/right Test
    imu_res = imu.collect_imu_data()
    if imu_res == False:
        print("\nLeft turn detected\n")
    elif imu_res == True:
        print("\nRight turn detected\n")
    # Return value was None
    else:
        print("\nNo turn detected\n")

    # # Shake Test
    # imu_res = imu.detect_shake()
    # if imu_res:
    #     print("Shake detected")
    # else:
    #     print("No shake detected")
        
    time.sleep(3)
