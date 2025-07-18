from enum import Enum


class CurrentStatusEnum(str, Enum):
    ALL = "All"
    CURRENT = "Current"
    DISCONTINUED = "Discontinued"

    def __str__(self) -> str:
        return str(self.value)
