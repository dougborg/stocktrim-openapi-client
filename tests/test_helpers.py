"""Tests for domain helper classes.

These tests verify that helper classes are properly initialized and
have access to the client. Full API integration tests should be done
separately with real or mocked API responses.
"""


class TestHelpersIntegration:
    """Test helper integration with StockTrimClient."""

    def test_products_helper_exists(self, stocktrim_client):
        """Test products helper is accessible."""
        assert hasattr(stocktrim_client, "products")
        assert stocktrim_client.products is not None

    def test_customers_helper_exists(self, stocktrim_client):
        """Test customers helper is accessible."""
        assert hasattr(stocktrim_client, "customers")
        assert stocktrim_client.customers is not None

    def test_suppliers_helper_exists(self, stocktrim_client):
        """Test suppliers helper is accessible."""
        assert hasattr(stocktrim_client, "suppliers")
        assert stocktrim_client.suppliers is not None

    def test_sales_orders_helper_exists(self, stocktrim_client):
        """Test sales_orders helper is accessible."""
        assert hasattr(stocktrim_client, "sales_orders")
        assert stocktrim_client.sales_orders is not None

    def test_purchase_orders_helper_exists(self, stocktrim_client):
        """Test purchase_orders helper is accessible."""
        assert hasattr(stocktrim_client, "purchase_orders")
        assert stocktrim_client.purchase_orders is not None

    def test_inventory_helper_exists(self, stocktrim_client):
        """Test inventory helper is accessible."""
        assert hasattr(stocktrim_client, "inventory")
        assert stocktrim_client.inventory is not None

    def test_locations_helper_exists(self, stocktrim_client):
        """Test locations helper is accessible."""
        assert hasattr(stocktrim_client, "locations")
        assert stocktrim_client.locations is not None

    def test_helpers_have_base_methods(self, stocktrim_client):
        """Test helpers have expected core methods."""
        # Products
        assert hasattr(stocktrim_client.products, "get_all")
        assert hasattr(stocktrim_client.products, "create")
        assert hasattr(stocktrim_client.products, "find_by_code")
        assert hasattr(stocktrim_client.products, "search")
        assert hasattr(stocktrim_client.products, "exists")

        # Customers
        assert hasattr(stocktrim_client.customers, "get_all")
        assert hasattr(stocktrim_client.customers, "get")
        assert hasattr(stocktrim_client.customers, "exists")
        assert hasattr(stocktrim_client.customers, "find_or_create")

        # Suppliers
        assert hasattr(stocktrim_client.suppliers, "get_all")
        assert hasattr(stocktrim_client.suppliers, "create")
        assert hasattr(stocktrim_client.suppliers, "find_by_code")
        assert hasattr(stocktrim_client.suppliers, "create_one")
        assert hasattr(stocktrim_client.suppliers, "exists")

        # Sales Orders
        assert hasattr(stocktrim_client.sales_orders, "get_all")
        assert hasattr(stocktrim_client.sales_orders, "create")
        assert hasattr(stocktrim_client.sales_orders, "get_for_product")
        assert hasattr(stocktrim_client.sales_orders, "delete_for_product")

        # Purchase Orders
        assert hasattr(stocktrim_client.purchase_orders, "get_all")
        assert hasattr(stocktrim_client.purchase_orders, "create")
        assert hasattr(stocktrim_client.purchase_orders, "find_by_reference")
        assert hasattr(stocktrim_client.purchase_orders, "exists")

        # Inventory
        assert hasattr(stocktrim_client.inventory, "set")
        assert hasattr(stocktrim_client.inventory, "set_for_product")

        # Locations
        assert hasattr(stocktrim_client.locations, "get_all")
        assert hasattr(stocktrim_client.locations, "create")

    def test_helpers_lazy_loaded(self, stocktrim_client):
        """Test that helpers are lazy-loaded."""
        # First access creates the helper
        products1 = stocktrim_client.products
        # Second access returns the same instance
        products2 = stocktrim_client.products
        assert products1 is products2
