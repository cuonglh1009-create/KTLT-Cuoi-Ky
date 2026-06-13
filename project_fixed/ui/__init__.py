"""
Gói ui chứa giao diện người dùng cho Hệ thống Quản lý Hóa đơn.

Gói này chứa:
- gui: Giao diện đồ họa Tkinter
- Các thành phần UI tương lai (CLI, web interface)
"""

# Xuất cụ thể hàm start_gui 
from .gui import start_gui

__all__ = ['gui', 'start_gui'] 