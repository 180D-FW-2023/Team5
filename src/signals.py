from enum import IntEnum

class Signals(IntEnum):
    END_CONNECTION = 0
    INIT_FT_STREAMED = 1
    END_FT_STREAMED = 2
    DATA_SENT = 3
    FILE_SENT = 4
    # add future data transfers for imus and stuff here