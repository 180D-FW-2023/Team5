from signals import Signals
from imu.imu_handler import ImuHandler
import time

imu = ImuHandler()

while True:
    # Left/right Test
    # imu_res = imu.collect_imu_data()
    # if imu_res == False:
    #     print("\nleft left left left\n")
    # elif imu_res == True:
    #     print("\nright right right right\n")
    # # Return value was None
    # else:
    #     print("\nno turn detected\n")

    # Shake Test
    imu_res = imu.detect_shake()
    if imu_res:
        print("SHAKE")
    else:
        print("no shake")
        
    time.sleep(3)
