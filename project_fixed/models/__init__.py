"""
Gói models chứa các mô hình dữ liệu cho Hệ thống Quản lý Hóa đơn.

Gói này export các dataclass chính:
- Product: Mô hình sản phẩm
- Customer: Mô hình khách hàng
- Invoice: Mô hình hóa đơn
- InvoiceItem: Mô hình mục hàng trong hóa đơn
"""

from .product import Product
from .customer import Customer
from .invoice import Invoice, InvoiceItem

__all__ = ['Product', 'Customer', 'Invoice', 'InvoiceItem']
