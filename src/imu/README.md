
# Code Information for imu directory

This directory contains the software backend for the implementation of kinematic controls. All of the functions in this file were taken from the BerryIMU open-source code except for the imu_handler.py, for which we took inspiration from the BerryIMU code.

  ```IMU.py``` - Driver code for Berry IMU v3 detection and measurements.

- detectIMU(): detect which version of BerryIMU is connected using the 'who am i' register. BerryIMUv3 uses the LSM6DSL and LIS3MDL.
- writeByte(): writes a byte to a register/address
- readACC functions: reads accelerometer data in all three dimensions
- readGYR functions: reads gyroscope data in all three dimensions
- readMAG functions: reads magnetometer data in all three dimensions
- initIMU(): initializes the IMU for collecting data

  ```LIS3MDL.py``` and ```LSM6DSL.py``` - Addresses for reading from the IMU.

  ```calibrateBerryIMU.py``` - Runs calibration script to get maximum values in each dimension. Collects accelerometer, gyroscope, and magnetometer data until user kills the program.

  ```imu_handler.py``` - Top level IMU file that initializes IMU and has left/right and shake detection algorithms.

- init(): initializes the ImuHandler class by detecting the IMU and running the initialization function in IMU.py
- calibrate_imu_data(): runs the calibration code for 20 iterations and calculates average values
- collect_imu_data_with_cal(): collects accelerometer/gryoscope data for 35 iterations and compare ending averages to averages calculated from calibrate_imu_data() to determine left or right turn.
- collect_imu_data(): collects accelerometer/gryoscope data for 35 iterations; the first 5 calculate starting averages, the next 20 are when the user moves the toy, and the last 10 calculate ending averages to determine left or right turn.
- detect_shake(): collects accelerometer/gryoscope data for 20 iterations and sums up magnitude differences in values for X and Y dimensions; compares to a threshold to determine if the user shook the toy.

The code in this function works generally well. Occasionally the polarity of the IMU directions switches, so this could be accounted for by running more calibration before each IMU data collection. Additionally, the threshold values could be adjusted based on calibration. Finally, more types of motions could be classified with the IMU for an even more interactive game.