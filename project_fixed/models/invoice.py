"""
Mô hình Hóa đơn cho Hệ thống Quản lý Hóa đơn.

Module này định nghĩa các dataclass cho hóa đơn bao gồm:
- InvoiceItem: Đại diện cho một mục hàng trong hóa đơn
- Invoice: Đại diện cho toàn bộ hóa đơn với danh sách các mục hàng

Các model này cung cấp các property để tính toán tự động
tổng tiền và số lượng mặt hàng.
"""

from dataclasses import dataclass, field
import datetime
from typing import List

@dataclass
class InvoiceItem:
    """
    Mô hình dữ liệu mặt hàng trong hóa đơn.
    
    Thuộc tính:
        product_id (str): Mã sản phẩm
        quantity (int): Số lượng
        unit_price (float): Giá mỗi đơn vị
    """
    product_id: str
    quantity: int
    unit_price: float
    
    @property
    def total_price(self) -> float:
        """Tính tổng giá trị cho mặt hàng này."""
        return self.quantity * self.unit_price


@dataclass
class Invoice:
    """
    Mô hình dữ liệu Hóa đơn.
    
    Thuộc tính:
        invoice_id (str): Định danh duy nhất cho hóa đơn
        date (str): Ngày lập hóa đơn
        customer_name (str): Tên khách hàng
        items (List[InvoiceItem]): Danh sách các mặt hàng trong hóa đơn
    """
    invoice_id: str
    customer_name: str
    items: List[InvoiceItem] = field(default_factory=list)
    date: str = field(default_factory=lambda: datetime.datetime.now().strftime('%Y-%m-%d'))
    
    @property
    def total_amount(self) -> float:
        """Tính tổng giá trị của hóa đơn."""
        return sum(item.total_price for item in self.items)
    
    @property
    def total_items(self) -> int:
        """Tính tổng số mặt hàng trong hóa đơn."""
        return sum(item.quantity for item in self.items) 