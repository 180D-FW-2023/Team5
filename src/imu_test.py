from signals import Signals
from imu.imu_handler import ImuHandler
import time

imu = ImuHandler()

while True:
    imu_res = imu.collect_imu_data()
    if imu_res == False:
        print("\nleft left left left\n")
    elif imu_res == True:
        print("\nright right right right\n")
    # Return value was None
    else:
        print("\nno turn detected\n")
    time.sleep(3)
