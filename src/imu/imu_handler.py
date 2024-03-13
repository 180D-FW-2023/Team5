import sys
import time
import math
import imu.IMU as i
# from queue import Queue

RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070  # [deg/s/LSB]  If you change the dps for gyro, you need to upda>
AA =  0.40      # Complementary filter constant
NUM_CAL_ITERS = 20
NUM_ITERS = 35
NUM_SHAKE_ITERS = 20

class ImuHandler:
    def __init__(self,):
        # Calibration values
        self.magXmin = -2300
        self.magYmin = -279
        self.magZmin = -3340
        self.magXmax = 1062
        self.magYmax = 2343
        self.magZmax = -564
        self.avg_angle = 0

        self.imu_enabled = True
        # self.res_queue = Queue()

        # Comment out to not use IMU
        i.detectIMU()     # Detect if BerryIMU is connected.
        if(i.BerryIMUversion == 99):
            print(" No BerryIMU found... exiting ")
            self.imu_enabled = False
        i.initIMU()       # Initialise the accelerometer, gyroscope and compass

    # def collect_imu_data_wrapper(self):
    #     result = self.collect_imu_data()
    #     self.res_queue.put(result)
        
    def calibrate_imu_data(self):
        if self.imu_enabled == False:
            return None
        
        print("\nCalibrating\n")
        
        gyroXangle = 0.0
        gyroYangle = 0.0
        gyroZangle = 0.0
        CFangleX = 0.0
        CFangleY = 0.0
        SumCFangleY = 0.0
        past_time = time.time()

        for j in range(NUM_CAL_ITERS):
            output_str = ""

            #Read the accelerometer,gyroscope and magnetometer values
            ACCx = i.readACCx()
            ACCy = i.readACCy()
            ACCz = i.readACCz()
            GYRx = i.readGYRx()
            GYRy = i.readGYRy()
            GYRz = i.readGYRz()

            # Display loop time
            curr_time = time.time()
            loop_time = curr_time - past_time
            output_str += "Loop time: %5.2f " % (loop_time)
            past_time = curr_time

            #Convert Gyro raw to degrees per second
            rate_gyr_x =  GYRx * G_GAIN
            rate_gyr_y =  GYRy * G_GAIN
            rate_gyr_z =  GYRz * G_GAIN


            #Calculate the angles from the gyro.
            gyroXangle+=rate_gyr_x*loop_time
            gyroYangle+=rate_gyr_y*loop_time
            gyroZangle+=rate_gyr_z*loop_time
        
            #Convert Accelerometer values to degrees
            AccXangle =  (math.atan2(ACCy,ACCz)*RAD_TO_DEG)
            AccYangle =  (math.atan2(ACCz,ACCx)+M_PI)*RAD_TO_DEG

             #convert the values to -180 and +180
            if AccYangle > 90:
                AccYangle -= 270.0
            else:
                AccYangle += 90.0

            #Complementary filter used to combine the accelerometer and gyro values.
            CFangleX=AA*(CFangleX+rate_gyr_x*loop_time) +(1 - AA) * AccXangle
            CFangleY=AA*(CFangleY+rate_gyr_y*loop_time) +(1 - AA) * AccYangle

            if j == 0:
                first_CFangleY = CFangleY
            
            SumCFangleY += CFangleY

            output_str +="\t# CFangleY Angle %5.2f #" % (CFangleY)

            print(output_str)

            time.sleep(0.03)
        
        print("First Y angle: %5.2f \nLast Y angle: %5.2f" % (first_CFangleY,CFangleY)) 
        self.avg_angle = SumCFangleY / NUM_CAL_ITERS
        print("Average Ending angle: %5.2f" % (self.avg_angle))

        print("\n Done Calibrating\n")
        return True
    
    
    def collect_imu_data_with_cal(self):

        if self.imu_enabled == False:
            return None
        
        gyroXangle = 0.0
        gyroYangle = 0.0
        gyroZangle = 0.0
        CFangleX = 0.0
        CFangleY = 0.0
        SumCFangleY = 0.0
        past_time = time.time()

        print("\nStarting averaging\n")

        for j in range(NUM_ITERS):
            output_str = ""
            
            #Read the accelerometer,gyroscope and magnetometer values
            ACCx = i.readACCx()
            ACCy = i.readACCy()
            ACCz = i.readACCz()
            GYRx = i.readGYRx()
            GYRy = i.readGYRy()
            GYRz = i.readGYRz()

            # Display loop time
            curr_time = time.time()
            loop_time = curr_time - past_time
            past_time = curr_time

            #Convert Gyro raw to degrees per second
            rate_gyr_x =  GYRx * G_GAIN
            rate_gyr_y =  GYRy * G_GAIN
            rate_gyr_z =  GYRz * G_GAIN


            #Calculate the angles from the gyro.
            gyroXangle+=rate_gyr_x*loop_time
            gyroYangle+=rate_gyr_y*loop_time
            gyroZangle+=rate_gyr_z*loop_time
        
            #Convert Accelerometer values to degrees
            AccXangle =  (math.atan2(ACCy,ACCz)*RAD_TO_DEG)
            AccYangle =  (math.atan2(ACCz,ACCx)+M_PI)*RAD_TO_DEG

             #convert the values to -180 and +180
            if AccYangle > 90:
                AccYangle -= 270.0
            else:
                AccYangle += 90.0

            #Complementary filter used to combine the accelerometer and gyro values.
            CFangleX=AA*(CFangleX+rate_gyr_x*loop_time) +(1 - AA) * AccXangle
            CFangleY=AA*(CFangleY+rate_gyr_y*loop_time) +(1 - AA) * AccYangle

            SumCFangleY += CFangleY

            output_str +="\t# CFangleY Angle %5.2f #" % (CFangleY)

            print(output_str)

            time.sleep(0.03)
        
        avg_ending_angle = 1.0 * SumCFangleY / NUM_ITERS
        print("Average Ending angle: %5.2f" % (avg_ending_angle))
        if avg_ending_angle - self.avg_angle > 30:
            print("Right turn detected")
            return True
        elif avg_ending_angle - self.avg_angle > 30:
            print("Left turn detected")
            return False
        return None


    def collect_imu_data(self):

        if self.imu_enabled == False:
            return None
        
        gyroXangle = 0.0
        gyroYangle = 0.0
        gyroZangle = 0.0
        CFangleX = 0.0
        CFangleY = 0.0
        first_CFangleY = 0.0
        SumCFangleY = 0.0
        past_time = time.time()

        for j in range(NUM_ITERS):
            output_str = ""
            
            if j == 5:
                print("\nStarting measurements\n")
            elif j == 25:
                print("\nStarting averaging\n")

            #Read the accelerometer,gyroscope and magnetometer values
            ACCx = i.readACCx()
            ACCy = i.readACCy()
            ACCz = i.readACCz()
            GYRx = i.readGYRx()
            GYRy = i.readGYRy()
            GYRz = i.readGYRz()

            # Display loop time
            curr_time = time.time()
            loop_time = curr_time - past_time
            if j >= 5 and j < 25:
                output_str += "Loop time: %5.2f " % (loop_time)
            past_time = curr_time

            #Convert Gyro raw to degrees per second
            rate_gyr_x =  GYRx * G_GAIN
            rate_gyr_y =  GYRy * G_GAIN
            rate_gyr_z =  GYRz * G_GAIN


            #Calculate the angles from the gyro.
            gyroXangle+=rate_gyr_x*loop_time
            gyroYangle+=rate_gyr_y*loop_time
            gyroZangle+=rate_gyr_z*loop_time
        
            #Convert Accelerometer values to degrees
            AccXangle =  (math.atan2(ACCy,ACCz)*RAD_TO_DEG)
            AccYangle =  (math.atan2(ACCz,ACCx)+M_PI)*RAD_TO_DEG

             #convert the values to -180 and +180
            if AccYangle > 90:
                AccYangle -= 270.0
            else:
                AccYangle += 90.0

            #Complementary filter used to combine the accelerometer and gyro values.
            CFangleX=AA*(CFangleX+rate_gyr_x*loop_time) +(1 - AA) * AccXangle
            CFangleY=AA*(CFangleY+rate_gyr_y*loop_time) +(1 - AA) * AccYangle

            if j < 5:
                first_CFangleY += CFangleY
            elif j >= 25:
                SumCFangleY += CFangleY

            output_str +="\t# CFangleY Angle %5.2f #" % (CFangleY)

            print(output_str)

            time.sleep(0.03)
        
        first_CFangleY /= 5.0
        print("First Y angle: %5.2f \nLast Y angle: %5.2f" % (first_CFangleY,CFangleY)) 
        avg_ending_angle = SumCFangleY / 10.0
        print("Average Ending angle: %5.2f" % (avg_ending_angle))
        if avg_ending_angle - first_CFangleY > 35:
            print("Right turn detected")
            return True
        elif first_CFangleY - avg_ending_angle > 25:
            print("Left turn detected")
            return False
        return None


    def detect_shake(self):

        if self.imu_enabled == False:
            return None
        
        gyroXangle = 0.0
        gyroYangle = 0.0
        gyroZangle = 0.0
        CFangleX = 0.0
        CFangleY = 0.0
        sum_distances = 0.0
        past_time = time.time()

        for j in range(NUM_SHAKE_ITERS):
            output_str = ""

            #Read the accelerometer,gyroscope and magnetometer values
            ACCx = i.readACCx()
            ACCy = i.readACCy()
            ACCz = i.readACCz()
            GYRx = i.readGYRx()
            GYRy = i.readGYRy()
            GYRz = i.readGYRz()

            # Display loop time
            curr_time = time.time()
            loop_time = curr_time - past_time
            output_str += "Loop time: %5.2f " % (loop_time)
            past_time = curr_time

            #Convert Gyro raw to degrees per second
            rate_gyr_x =  GYRx * G_GAIN
            rate_gyr_y =  GYRy * G_GAIN
            rate_gyr_z =  GYRz * G_GAIN


            #Calculate the angles from the gyro.
            gyroXangle+=rate_gyr_x*loop_time
            gyroYangle+=rate_gyr_y*loop_time
            gyroZangle+=rate_gyr_z*loop_time
        
            #Convert Accelerometer values to degrees
            AccXangle =  (math.atan2(ACCy,ACCz)*RAD_TO_DEG)
            AccYangle =  (math.atan2(ACCz,ACCx)+M_PI)*RAD_TO_DEG

             #convert the values to -180 and +180
            if AccYangle > 90:
                AccYangle -= 270.0
            else:
                AccYangle += 90.0

            prev_CFangleX = CFangleX
            prev_CFangleY = CFangleY

            #Complementary filter used to combine the accelerometer and gyro values.
            CFangleX=AA*(CFangleX+rate_gyr_x*loop_time) +(1 - AA) * AccXangle
            CFangleY=AA*(CFangleY+rate_gyr_y*loop_time) +(1 - AA) * AccYangle

            if j == 0:
                first_CFangleY = CFangleY
                first_CFangleX = CFangleX
            else:
                sum_distances += abs(CFangleX - prev_CFangleX)
                sum_distances += abs(CFangleY - prev_CFangleY)

            output_str +="\t# Sum Distances %5.2f #" % (sum_distances)

            print(output_str)

            time.sleep(0.03)
        
        print("First X angle: %5.2f \nFirst Y angle: %5.2f" % (first_CFangleX, first_CFangleY)) 
        print("Sum distances: %5.2f" % (sum_distances))
        if sum_distances > 500:
            print("Shake detected.")
            return True
        
        return False


if __name__ == '__main__':
    myimu = ImuHandler()
    myimu.collect_imu_data()
            
