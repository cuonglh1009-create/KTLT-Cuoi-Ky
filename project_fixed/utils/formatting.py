#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Các hàm tiện ích định dạng cho Hệ thống Quản lý Hóa đơn.

Module này cung cấp các hàm để định dạng dữ liệu hiển thị
trước người dùng một cách chuyên nghiệp và nhất quán.
Bao gồm định dạng:
- Tiền tệ với dấu phân cách hàng nghìn
- Ngày tháng và số điện thoại Việt Nam
- Mã sản phẩm và tên khách hàng
- Số hóa đơn chuẩn
"""

from datetime import datetime
from typing import Union, Optional

def format_currency(amount: Union[int, float]) -> str:
    """
    Định dạng số tiền với dấu phân cách hàng nghìn và hai chữ số thập phân.
    
    Tham số:
        amount: Số tiền cần định dạng
        
    Trả về:
        Chuỗi định dạng của số tiền
    """
    try:
        return f"{float(amount):,.2f} VNĐ"
    except (ValueError, TypeError):
        return "0.00 VNĐ"

def format_date(date: Union[str, datetime], input_format: str = "%Y-%m-%d", output_format: str = "%d/%m/%Y") -> str:
    """
    Định dạng ngày tháng.
    
    Tham số:
        date: Ngày tháng cần định dạng (chuỗi hoặc datetime)
        input_format: Định dạng đầu vào (nếu date là chuỗi)
        output_format: Định dạng đầu ra
        
    Trả về:
        Chuỗi ngày tháng đã định dạng
    """
    try:
        if date is None:
            return ""
        if isinstance(date, str):
            if not date.strip():  # Empty or whitespace-only string
                return ""
            date = datetime.strptime(date, input_format)
        return date.strftime(output_format)
    except (ValueError, TypeError, AttributeError):
        return ""

def format_phone_number(phone: str) -> str:
    """
    Định dạng số điện thoại Việt Nam.
    
    Tham số:
        phone: Số điện thoại cần định dạng
        
    Trả về:
        Chuỗi số điện thoại đã định dạng
    """
    try:
        # Loại bỏ tất cả ký tự không phải số
        numbers = ''.join(filter(str.isdigit, phone))
        if len(numbers) == 10:
            return f"{numbers[:3]} {numbers[3:6]} {numbers[6:]}"
        return phone
    except (ValueError, TypeError):
        return phone

def format_product_id(product_id: str) -> str:
    """
    Định dạng mã sản phẩm.
    
    Tham số:
        product_id: Mã sản phẩm cần định dạng
        
    Trả về:
        Chuỗi mã sản phẩm đã định dạng
    """
    try:
        return product_id.strip().upper()
    except (ValueError, TypeError):
        return ""

def format_customer_name(name: str) -> str:
    """
    Định dạng tên khách hàng.
    
    Tham số:
        name: Tên khách hàng cần định dạng
        
    Trả về:
        Chuỗi tên khách hàng đã định dạng
    """
    try:
        # Loại bỏ khoảng trắng thừa và viết hoa chữ cái đầu
        words = name.strip().split()
        return ' '.join(word.capitalize() for word in words)
    except (ValueError, TypeError):
        return ""

def format_invoice_number(invoice_id: int) -> str:
    """
    Định dạng số hóa đơn.
    
    Tham số:
        invoice_id: ID hóa đơn cần định dạng
        
    Trả về:
        Chuỗi số hóa đơn đã định dạng
    """
    try:
        return f"INV{invoice_id:06d}"
    except (ValueError, TypeError):
        return "INV000000" 