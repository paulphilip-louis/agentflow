from enum import Enum, auto


class Status(Enum):
    PENDING = auto()
    COMPLETED = auto()
    FAILED = auto()