from enum import IntEnum

class Signals(IntEnum):
    END_CONNECTION = 0
    INIT_FT_STREAMED = 1
    END_FT_STREAMED = 2
    DATA_SENT = 3
    FILE_SENT = 4
    GAME_END = 5
    IMU_TURN_RIGHT = 6
    IMU_TURN_LEFT = 7
    IMU_ROUND = 8
    IMU_NO_TURN = 9
    RETRY_IMU = 10
    IMU_SHAKE_ROUND = 11
    IMU_SHAKE = 12
    IMU_NO_SHAKE = 13
    # add future data transfers for imus and stuff here
