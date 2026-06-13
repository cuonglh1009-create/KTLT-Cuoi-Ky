"""
Mô hình Khách hàng cho Hệ thống Quản lý Hóa đơn.
"""
from dataclasses import dataclass, field

@dataclass
class Customer:
    """
    Mô hình dữ liệu Khách hàng.

    Thuộc tính:
        customer_id (str): Mã khách hàng duy nhất
        name (str)       : Họ tên khách hàng
        phone (str)      : Số điện thoại
        address(str): Địa chỉ
    """
    customer_id: str
    name: str
    phone: str = ""
    address: str = ""

    def __post_init__(self):
        if not self.customer_id or not self.customer_id.strip():
            raise ValueError("Mã khách hàng không được để trống")
        if not self.name or not self.name.strip():
            raise ValueError("Tên khách hàng không được để trống")

    def display_name(self) -> str:
        """Trả về chuỗi hiển thị: ID - Tên."""
        return f"{self.customer_id} - {self.name}"
