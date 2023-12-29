from enum import Enum

class Signals(Enum):
    END_CONNECTION = 0
    INIT_FT_STREAMED = 1
    FT_IN_PROGRESS = 2
    END_FT_STREAMED = 3
    DATA_SENT = 4
    # add future data transfers for imus and stuff here