from enum import Enum


class PurchaseOrderStatusDto(str, Enum):
    APPROVED = "Approved"
    DRAFT = "Draft"
    RECEIVED = "Received"
    SENT = "Sent"

    def __str__(self) -> str:
        return str(self.value)
