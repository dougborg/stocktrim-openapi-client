from enum import IntEnum


class PurchaseOrderStatusDto(IntEnum):
    DRAFT = 0
    APPROVED = 1
    SENT = 2
    RECEIVED = 3

    def __str__(self) -> str:
        return str(self.value)
