from enum import Enum


class UserRole(str, Enum):
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    