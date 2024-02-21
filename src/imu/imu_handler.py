import sys
import time
import math
import IMU as i

RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070  # [deg/s/LSB]  If you change the dps for gyro, you need to upda>
AA =  0.40      # Complementary filter constant
NUM_ITERS = 30

class ImuHandler:
    def __init__(self,):
        # Calibration values
        self.magXmin = -2300
        self.magYmin = -279
        self.magZmin = -3340
        self.magXmax = 1062
        self.magYmax = 2343
        self.magZmax = -564

        i.detectIMU()     # Detect if BerryIMU is connected.
        if(i.BerryIMUversion == 99):
            print(" No BerryIMU found... exiting ")
            sys.exit()
        i.initIMU()       # Initialise the accelerometer, gyroscope and compass


    def collect_imu_data(self):

        gyroXangle = 0.0
        gyroYangle = 0.0
        gyroZangle = 0.0
        CFangleX = 0.0
        CFangleY = 0.0
        SumCFangleY = 0.0
        past_time = time.time()

        for j in range(NUM_ITERS):
            output_str = ""
            
            if j == 20:
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
            if j < 20:
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
            elif j > 19:
                SumCFangleY += CFangleY

            output_str +="\t# CFangleY Angle %5.2f #" % (CFangleY)

            print(output_str)

            time.sleep(0.03)
        
        print("First Y angle: %5.2f \nLast Y angle: %5.2f" % (first_CFangleY,CFangleY)) 
        avg_ending_angle = SumCFangleY / 10.0
        print("Average Ending angle: %5.2f" % (avg_ending_angle))
        if avg_ending_angle - first_CFangleY > 50:
            print("Right turn detected")
            return True
        elif first_CFangleY - avg_ending_angle > 50:
            print("Left turn detected")
            return False
        return None


            

# def collect_imu_data(self):
    
#     #Read the accelerometer,gyroscope and magnetometer values
#     ACCx = i.readACCx()
#     ACCy = i.readACCy()
#     ACCz = i.readACCz()
#     # GYRx = IMU.readGYRx()
#     # GYRy = IMU.readGYRy()
#     # GYRz = IMU.readGYRz()
#     # MAGx = IMU.readMAGx()
#     # MAGy = IMU.readMAGy()
#     # MAGz = IMU.readMAGz()
#     count = 0

#     while count < 500:
#         self.x_biases.append(ACCx)
#         self.z_biases.append(ACCz)
#         if count == 499:
#             self.x_bias = sum(self.x_biases)/len(self.x_biases)
#             self.z_bias = sum(self.z_biases)/len(self.z_biases)
#             print(str(self.x_bias))
#             print(str(self.z_bias))
#             time.sleep(2)
#         count += 1

#     for i in range(20):
#         ax = ACCx - self.x_bias
#         az = ACCz - self.z_bias
#         self.x_acc.append(ax)
#         self.z_acc.append(az)
#         if len(self.x_acc) < 20:
#             time.sleep(0.01)
#             continue
#         else:
#             print("-------------")
#             print("x: " + str(sum(self.x_acc)/len(self.x_acc)))
#             print("z: " + str(sum(self.z_acc)/len(self.z_acc)))
#             print("------------")
#             if abs(sum(self.x_acc)/len(self.x_acc)) > 500:
#                 print("forward push detected")
#             if abs(sum(self.z_acc)/(len(self.z_acc))) > 500:
#                 print("upwards lift detected")
#             self.x_acc.clear()
#             self.z_acc.clear()
#             time.sleep(0.25)
#             continue

# Kalman filter stuff below

# #Kalman filter variables
# Q_angle = 0.02
# Q_gyro = 0.0015
# R_angle = 0.005
# y_bias = 0.0
# x_bias = 0.0
# XP_00 = 0.0
# XP_01 = 0.0
# XP_10 = 0.0
# XP_11 = 0.0
# YP_00 = 0.0
# YP_01 = 0.0
# YP_10 = 0.0
# YP_11 = 0.0
# KFangleX = 0.0
# KFangleY = 0.0


# def kalmanFilterY ( accAngle, gyroRate, DT):
#     y=0.0
#     S=0.0

#     global KFangleY
#     global Q_angle
#     global Q_gyro
#     global y_bias
#     global YP_00
#     global YP_01
#     global YP_10
#     global YP_11

#     KFangleY = KFangleY + DT * (gyroRate - y_bias)

#     YP_00 = YP_00 + ( - DT * (YP_10 + YP_01) + Q_angle * DT )
#     YP_01 = YP_01 + ( - DT * YP_11 )
#     YP_10 = YP_10 + ( - DT * YP_11 )
#     YP_11 = YP_11 + ( + Q_gyro * DT )

#     y = accAngle - KFangleY
#     S = YP_00 + R_angle
#     K_0 = YP_00 / S
#     K_1 = YP_10 / S

#     KFangleY = KFangleY + ( K_0 * y )
#     y_bias = y_bias + ( K_1 * y )

#     YP_00 = YP_00 - ( K_0 * YP_00 )
#     YP_01 = YP_01 - ( K_0 * YP_01 )
#     YP_10 = YP_10 - ( K_1 * YP_00 )
#     YP_11 = YP_11 - ( K_1 * YP_01 )

#     return KFangleY


# def kalmanFilterX ( accAngle, gyroRate, DT):
#     x=0.0
#     S=0.0

#     global KFangleX
#     global Q_angle
#     global Q_gyro
#     global x_bias
#     global XP_00
#     global XP_01
#     global XP_10
#     global XP_11


#     KFangleX = KFangleX + DT * (gyroRate - x_bias)

#     XP_00 = XP_00 + ( - DT * (XP_10 + XP_01) + Q_angle * DT )
#     XP_01 = XP_01 + ( - DT * XP_11 )
#     XP_10 = XP_10 + ( - DT * XP_11 )
#     XP_11 = XP_11 + ( + Q_gyro * DT )

#     x = accAngle - KFangleX
#     S = XP_00 + R_angle
#     K_0 = XP_00 / S
#     K_1 = XP_10 / S

#     KFangleX = KFangleX + ( K_0 * x )
#     x_bias = x_bias + ( K_1 * x )

#     XP_00 = XP_00 - ( K_0 * XP_00 )
#     XP_01 = XP_01 - ( K_0 * XP_01 )
#     XP_10 = XP_10 - ( K_1 * XP_00 )
#     XP_11 = XP_11 - ( K_1 * XP_01 )

#     return KFangleX



