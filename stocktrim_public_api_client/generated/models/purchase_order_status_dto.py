from enum import Enum


class PurchaseOrderStatusDto(str, Enum):
    APPROVED = "Approved"
    DRAFT = "Draft"
    RECEIVED = "Received"
    SENT = "Sent"

    @classmethod
    def _missing_(cls, value):
        """Handle integer status codes from API.

        StockTrim API sometimes returns integer status codes instead of strings:
        0 = Draft, 1 = Approved, 2 = Sent, 3 = Received
        """
        if isinstance(value, int):
            mapping = {
                0: cls.DRAFT,
                1: cls.APPROVED,
                2: cls.SENT,
                3: cls.RECEIVED,
            }
            return mapping.get(value)
        return None

    def __str__(self) -> str:
        return str(self.value)
