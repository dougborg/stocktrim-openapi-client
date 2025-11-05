"""Server context for StockTrim MCP Server."""

from __future__ import annotations

from stocktrim_mcp_server.services.customers import CustomerService
from stocktrim_mcp_server.services.inventory import InventoryService
from stocktrim_mcp_server.services.locations import LocationService
from stocktrim_mcp_server.services.products import ProductService
from stocktrim_mcp_server.services.purchase_orders import PurchaseOrderService
from stocktrim_mcp_server.services.sales_orders import SalesOrderService
from stocktrim_mcp_server.services.suppliers import SupplierService
from stocktrim_public_api_client import StockTrimClient


class ServerContext:
    """Context object that holds the StockTrimClient and service layer for the server lifespan."""

    def __init__(self, client: StockTrimClient):
        """Initialize server context with StockTrimClient and services.

        Args:
            client: Initialized StockTrimClient instance
        """
        self.client = client

        # Service layer
        self.inventory = InventoryService(client)
        self.customers = CustomerService(client)
        self.locations = LocationService(client)
        self.products = ProductService(client)
        self.purchase_orders = PurchaseOrderService(client)
        self.sales_orders = SalesOrderService(client)
        self.suppliers = SupplierService(client)
