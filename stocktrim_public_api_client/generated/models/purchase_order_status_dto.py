from enum import StrEnum


class PurchaseOrderStatusDto(StrEnum):
    APPROVED = "Approved"
    DRAFT = "Draft"
    RECEIVED = "Received"
    SENT = "Sent"

    def __str__(self) -> str:
        return str(self.value)
