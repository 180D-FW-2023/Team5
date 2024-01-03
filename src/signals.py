from enum import IntEnum

class Signals(IntEnum):
    END_CONNECTION = 0
    INIT_FT_STREAMED = 1
    IN_PROGRESS_FT_STREAMED = 2
    END_FT_STREAMED = 3
    DATA_SENT = 4
    FILE_SENT = 5
    # add future data transfers for imus and stuff here