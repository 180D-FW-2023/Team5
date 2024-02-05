from enum import IntEnum

class Signals(IntEnum):
    END_CONNECTION = 0
    INIT_FT_STREAMED = 1
    END_FT_STREAMED = 2
    DATA_SENT = 3
    FILE_SENT = 4
    GAME_END = 5
    IMU_TURN_RIGHT = 
    IMU_TURN_LEFT = 7
    # add future data transfers for imus and stuff here
