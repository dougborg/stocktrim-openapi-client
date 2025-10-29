from enum import Enum


class ApiEnum(str, Enum):
    ACUMATICA = "Acumatica"
    AMAZONFBA = "AmazonFba"
    BIGCOMMERCE = "BigCommerce"
    CIN7 = "Cin7"
    CSVUPLOAD = "CsvUpload"
    DEAR = "Dear"
    FINALE = "Finale"
    FISHBOWL = "Fishbowl"
    INFLOW = "InFlow"
    KATANA = "Katana"
    MAGENTO = "Magento"
    MRPEASY = "MrpEasy"
    MYOB = "Myob"
    NETO = "Neto"
    ODOO = "Odoo"
    QUICKBOOKS = "Quickbooks"
    SELLERCLOUD = "Sellercloud"
    SHOPIFY = "Shopify"
    SKUVAULT = "SkuVault"
    SQUAREINVENTORY = "SquareInventory"
    STOCKTRIMINCOMINGAPI = "StockTrimIncomingApi"
    TRADEGECKO = "TradeGecko"
    UNLEASHED = "Unleashed"
    VEND = "Vend"
    WOOCOMMERCE = "WooCommerce"
    XERO = "Xero"
    ZOHO = "Zoho"

    def __str__(self) -> str:
        return str(self.value)
