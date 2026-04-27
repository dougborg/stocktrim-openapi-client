from enum import StrEnum


class CurrentStatusEnum(StrEnum):
    ALL = "All"
    CURRENT = "Current"
    DISCONTINUED = "Discontinued"

    def __str__(self) -> str:
        return str(self.value)
